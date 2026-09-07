"""
Dashboard del Bot de Ejecución.
Ejecutar con: python dashboard.py
"""

import ctypes
import json
import math
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

try:
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
except Exception:
    pass

BASE_DIR    = Path(__file__).resolve().parent
STATE_FILE  = BASE_DIR / "state" / "state.json"
LOG_FILE    = BASE_DIR / "logs"  / "exec_bot.log"
TRAIN_BASE  = BASE_DIR.parent / "botentrenamiento"
MODEL_PATH  = TRAIN_BASE / "models" / "model_latest.pkl"
METRICS_PATH = TRAIN_BASE / "models" / "metrics.json"

REFRESH_MS = 2000

# ── Paleta (igual que botentrenamiento) ───────────────────────────────────────
BG     = "#000000"
BG_C   = "#0a0a0a"
BG_C2  = "#111111"
BG_LOG = "#000000"
TEXT   = "#ffffff"
DIM    = "#1a1a1a"
DIM2   = "#2d6a7a"
CYAN   = "#6fc3df"
GREEN  = "#23d18b"
RED    = "#f14c4c"
YELLOW = "#f5f543"
BLUE   = "#3794ff"
PURPLE = "#d670d6"
WHITE  = "#ffffff"
ORANGE = "#e07c3e"
TEAL   = "#6fc3df"


def _lerp(c1: str, c2: str, t: float) -> str:
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    return (f"#{int(r1+(r2-r1)*t):02x}"
            f"{int(g1+(g2-g1)*t):02x}"
            f"{int(b1+(b2-b1)*t):02x}")


# ─────────────────────────────────────────────────────────────────────────────
#  Widgets reutilizados del botentrenamiento
# ─────────────────────────────────────────────────────────────────────────────

class PulseRing(tk.Canvas):
    RINGS = 3
    def __init__(self, parent, size=12, color=DIM2, **kw):
        kw.setdefault("bg", BG)
        sz = size + 22
        super().__init__(parent, width=sz, height=sz, highlightthickness=0, bd=0, **kw)
        self._size = size; self._color = color
        self._phase = [i * (2 * math.pi / self.RINGS) for i in range(self.RINGS)]
        self._alive = True; self._tick()

    def _tick(self):
        self.delete("all")
        sz = self.winfo_width() or (self._size + 22); cx = cy = sz // 2; r = self._size // 2
        for i in range(self.RINGS):
            self._phase[i] += 0.08
            t = (math.sin(self._phase[i]) + 1) / 2; rr = r + 3 + int(t * 8)
            self.create_oval(cx-rr, cy-rr, cx+rr, cy+rr,
                             fill="", outline=_lerp(BG, self._color, (1-t)*0.55), width=1)
        self.create_oval(cx-r, cy-r, cx+r, cy+r, fill=self._color, outline="")
        self.create_oval(cx-r//2, cy-r//2, cx+r//2, cy+r//2,
                         fill=_lerp(self._color, WHITE, 0.45), outline="")
        if self._alive: self.after(35, self._tick)

    def set_color(self, c): self._color = c
    def destroy(self): self._alive = False; super().destroy()


class NeonCard(tk.Canvas):
    INSET = 8
    def __init__(self, parent, accent=CYAN, auto_height=False, **kw):
        kw.setdefault("bg", BG)
        super().__init__(parent, highlightthickness=0, bd=0, **kw)
        self._accent = accent; self._auto_h = auto_height
        self._phase = 0.0; self._alive = True; self._last_fh = 0
        self._frame = tk.Frame(self, bg=BG_C)
        self._wid = self.create_window(self.INSET, self.INSET, anchor="nw", window=self._frame)
        self.bind("<Configure>", self._on_cfg)
        if self._auto_h: self._frame.bind("<Configure>", self._sync_h)
        self._glow_tick()

    def _sync_h(self, ev):
        if abs(ev.height - self._last_fh) < 2: return
        self._last_fh = ev.height
        self.configure(height=ev.height + 2 * self.INSET)

    def _on_cfg(self, ev):
        iw = max(4, ev.width - 2 * self.INSET)
        if self._auto_h:
            self.itemconfig(self._wid, width=iw)
        else:
            self.itemconfig(self._wid, width=iw, height=max(4, ev.height - 2*self.INSET))
        self._draw(ev.width, ev.height)

    def _draw(self, w=None, h=None):
        self.delete("brd"); w = w or self.winfo_width(); h = h or self.winfo_height()
        if w < 10 or h < 10: return
        t = (math.sin(self._phase) + 1) / 2; gi = 0.22 + t * 0.48
        self.create_rectangle(0, 0, w, h, fill=BG_C, outline="", tags="brd")
        for off, alpha in ((2, 0.18), (1, 0.80), (0, 0.42)):
            c = _lerp(BG, self._accent, gi * alpha)
            self.create_rectangle(off, off, w-off, h-off, fill="", outline=c, width=1, tags="brd")
        bright = _lerp(BG_C, self._accent, gi * 0.95)
        self.create_line(10, 1, w-10, 1, fill=bright, width=2, tags="brd")
        sz = 8; cc = _lerp(BG, self._accent, min(1.0, gi * 1.4))
        for x, y, dx, dy in [(0,0,sz,0),(0,0,0,sz),(w,0,-sz,0),(w,0,0,sz),
                              (0,h,sz,0),(0,h,0,-sz),(w,h,-sz,0),(w,h,0,-sz)]:
            self.create_line(x, y, x+dx, y+dy, fill=cc, width=2, tags="brd")

    def _glow_tick(self):
        if not self._alive: return
        self._phase += 0.045; self._draw()
        self.after(45, self._glow_tick)

    def set_accent(self, c): self._accent = c
    @property
    def frame(self): return self._frame
    def destroy(self): self._alive = False; super().destroy()


class TickerLabel(tk.Label):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._cur = 0.0; self._tgt = 0.0; self._fmt = lambda v: f"{v:.3f}"; self._anim = False

    def animate_to(self, value, fmt_fn, color=None):
        if color: self.config(fg=color)
        if not isinstance(value, (int, float)):
            self._anim = False; self.config(text=str(value)); return
        self._tgt = float(value); self._fmt = fmt_fn
        if not self._anim: self._step()

    def _step(self):
        diff = self._tgt - self._cur
        if abs(diff) < max(abs(self._tgt)*0.003, 0.00005):
            self._cur = self._tgt; self._anim = False
            try: self.config(text=self._fmt(self._cur))
            except Exception: pass
            return
        self._anim = True; self._cur += diff * 0.14
        try: self.config(text=self._fmt(self._cur))
        except Exception: pass
        self.after(16, self._step)


class NeonButton(tk.Canvas):
    def __init__(self, parent, text, command, color=BLUE, fg=WHITE, bw=160, bh=40, radius=7, **kw):
        kw["bg"] = BG
        super().__init__(parent, width=bw, height=bh, highlightthickness=0, bd=0, cursor="hand2", **kw)
        self._text=text; self._cmd=command; self._color=color; self._fg=fg
        self._radius=radius; self._bw=bw; self._bh=bh
        self._enabled=True; self._hover=False; self._pressed=False
        self._sweep=-0.3; self._sweeping=False; self._alive=True
        self.bind("<Enter>", self._on_enter); self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press); self.bind("<ButtonRelease-1>", self._on_release)
        self._draw()

    def _draw(self):
        self.delete("all"); w, h, r = self._bw, self._bh, self._radius
        if not self._enabled:
            fill=_lerp(self._color,BG,0.78); tc=_lerp(self._fg,BG,0.65); border=_lerp(self._color,BG,0.60)
        elif self._pressed:
            fill=_lerp(self._color,"#000000",0.25); tc=self._fg; border=self._color
        elif self._hover:
            fill=_lerp(self._color,WHITE,0.12); tc=self._fg; border=_lerp(self._color,WHITE,0.5)
        else:
            fill=self._color; tc=self._fg; border=_lerp(self._color,WHITE,0.3)
        pts=[r,0,w-r,0,w,0,w,r,w,h-r,w,h,w-r,h,r,h,0,h,0,h-r,0,r,0,0]
        self.create_polygon(pts, smooth=True, fill=fill, outline="")
        if self._hover and self._enabled and not self._pressed:
            sw=w//3; sx=int((w+sw*1.6)*self._sweep-sw//2)
            self.create_rectangle(sx,0,sx+sw,h, fill=_lerp(fill,WHITE,0.28), outline="")
        if self._enabled and not self._pressed:
            self.create_rectangle(r,0,w-r,h//3, fill=_lerp(fill,WHITE,0.15), outline="")
        if self._hover and self._enabled:
            self.create_polygon(pts, smooth=True, fill="", outline=border, width=1)
        self.create_text(w//2, h//2, text=self._text, fill=tc,
                         font=("Segoe UI", 9, "bold"), anchor="center")

    def _start_sweep(self):
        self._sweep=-0.3; self._sweeping=True; self._do_sweep()

    def _do_sweep(self):
        if not self._hover or not self._alive: self._sweeping=False; return
        self._sweep+=0.042; self._draw()
        if self._sweep < 1.35: self.after(14, self._do_sweep)
        else: self._sweeping=False

    def _on_enter(self, _):
        if self._enabled: self._hover=True
        if not self._sweeping: self._start_sweep()

    def _on_leave(self, _): self._hover=False; self._pressed=False; self._draw()
    def _on_press(self, _):
        if self._enabled: self._pressed=True; self._draw()

    def _on_release(self, _):
        if self._enabled and self._pressed:
            self._pressed=False; self._hover=True; self._draw(); self._cmd()

    def set_enabled(self, v): self._enabled=v; self._hover=False; self._pressed=False; self._draw()
    def set_text(self, t): self._text=t; self._draw()
    def set_color(self, c): self._color=c; self._draw()
    def destroy(self): self._alive=False; super().destroy()


class NeonScrollbar(tk.Canvas):
    W=8; THUMB=4; THUMB_H=6
    def __init__(self, parent, command=None, color=DIM2, bg=BG_C, orient="vertical", **kw):
        self._orient=orient
        if orient=="horizontal":
            super().__init__(parent,height=self.W,bg=bg,highlightthickness=0,bd=0,cursor="arrow",**kw)
        else:
            super().__init__(parent,width=self.W,bg=bg,highlightthickness=0,bd=0,cursor="arrow",**kw)
        self._cmd=command; self._color=color; self._bg=bg
        self._f0=0.0; self._f1=1.0; self._hover=False; self._drag_p=None; self._drag_f=None
        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<Enter>", lambda e: (setattr(self,"_hover",True), self._draw()))
        self.bind("<Leave>", lambda e: (setattr(self,"_hover",False), self._draw()))
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", lambda e: (setattr(self,"_drag_p",None),))
        self.bind("<MouseWheel>", lambda e: self._cmd and self._cmd("scroll", -1 if e.delta>0 else 1, "units"))

    def set(self, first, last): self._f0=float(first); self._f1=float(last); self._draw()

    def _draw(self):
        self.delete("all")
        cw = self.winfo_width()  or 200
        ch = self.winfo_height() or self.W
        tc = _lerp(self._color, WHITE, 0.35 if self._hover else 0.0)
        tr = _lerp(self._bg, WHITE, 0.04)

        if self._orient == "vertical":
            if ch < 4: return
            mx = cw // 2
            self.create_line(mx, 4, mx, ch-4, fill=tr, width=1)
            if self._f1 - self._f0 >= 0.999: return
            tw  = self.THUMB_H if self._hover else self.THUMB
            tx0 = (cw - tw) // 2;  tx1 = tx0 + tw
            ty0 = max(4,    int(ch * self._f0) + 2)
            ty1 = min(ch-4, max(ty0 + 20, int(ch * self._f1) - 2))
            self.create_rectangle(tx0, ty0, tx1, ty1, fill=tc, outline="")
        else:  # horizontal
            if cw < 4: return
            my = ch // 2
            self.create_line(4, my, cw-4, my, fill=tr, width=1)
            if self._f1 - self._f0 >= 0.999: return
            th  = self.THUMB_H if self._hover else self.THUMB
            ty0 = (ch - th) // 2;  ty1 = ty0 + th
            tx0 = max(4,    int(cw * self._f0) + 2)
            tx1 = min(cw-4, max(tx0 + 20, int(cw * self._f1) - 2))
            self.create_rectangle(tx0, ty0, tx1, ty1, fill=tc, outline="")

    def _pos(self, ev):
        return ev.x if self._orient == "horizontal" else ev.y

    def _size(self):
        return (self.winfo_width() if self._orient == "horizontal"
                else self.winfo_height())

    def _on_press(self, ev):
        cs = self._size(); pos = self._pos(ev)
        p0 = int(cs * self._f0); p1 = int(cs * self._f1)
        if p0 <= pos <= p1:
            self._drag_p = pos; self._drag_f = self._f0
        elif self._cmd:
            self._cmd("moveto", pos/cs - (self._f1-self._f0)/2)

    def _on_drag(self, ev):
        if self._drag_p is None or not self._cmd: return
        cs = self._size(); diff = (self._pos(ev) - self._drag_p) / cs
        self._cmd("moveto", self._drag_f + diff)


class Spinner(tk.Canvas):
    def __init__(self, parent, size=20, color=YELLOW, **kw):
        kw.setdefault("bg", BG)
        super().__init__(parent,width=size,height=size,highlightthickness=0,bd=0,**kw)
        self._size=size; self._color=color; self._angle=0.0; self._alive=True; self._tick()

    def _tick(self):
        self.delete("all"); cx=cy=self._size//2; r=cx-2; segs=10
        for i in range(segs):
            a1=math.radians(self._angle+i*(360/segs)); a2=a1+math.radians(360/segs*0.65)
            self.create_arc(cx-r,cy-r,cx+r,cy+r,start=math.degrees(a1),
                            extent=math.degrees(a2-a1),style="arc",
                            outline=_lerp(BG,self._color,(i/segs)**0.6),width=3)
        self._angle=(self._angle+8)%360
        if self._alive: self.after(28, self._tick)

    def set_color(self, c): self._color=c
    def destroy(self): self._alive=False; super().destroy()


class WinBtn(tk.Canvas):
    SIZE=13
    def __init__(self, parent, symbol, command, hover_color, **kw):
        kw.setdefault("bg", BG)
        super().__init__(parent,width=self.SIZE,height=self.SIZE,
                         highlightthickness=0,bd=0,cursor="hand2",**kw)
        self._sym=symbol; self._cmd=command; self._hc=hover_color; self._hov=False
        self.bind("<Enter>", lambda e: self._hover(True))
        self.bind("<Leave>", lambda e: self._hover(False))
        self.bind("<ButtonRelease-1>", lambda e: self._cmd())
        self._draw()

    def _hover(self, v): self._hov=v; self._draw()
    def _draw(self):
        self.delete("all"); sz=self.SIZE
        if self._hov:
            self.create_oval(0,0,sz,sz,fill=self._hc,outline="")
            self.create_text(sz//2,sz//2,text=self._sym,fill=WHITE,
                             font=("Segoe UI",6,"bold"),anchor="center")
        else:
            self.create_oval(1,1,sz-1,sz-1,fill=_lerp(BG,DIM2,0.7),outline="")


# ─────────────────────────────────────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

class Dashboard:
    def __init__(self, root: tk.Tk):
        self.root      = root
        self._process  = None
        self._scan_x   = 0.0
        self._hex_ph   = 0.0
        self._maximized  = False
        self._normal_geo = None
        self._drag_ox = self._drag_oy = 0
        self._rz_ox = self._rz_oy = self._rz_ow = self._rz_oh = 0

        root.title("Bot Ejecución — Monitor")
        root.configure(bg=BG)
        root.overrideredirect(True)

        sw = root.winfo_screenwidth(); sh = root.winfo_screenheight()
        w  = max(860, min(1120, int(sw * 0.82)))
        h  = max(620, min(int(sh * 0.88), sh - 60))
        root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        root.minsize(780, 560)

        self._build_ui()
        self._refresh()
        root.after(100, self._fix_taskbar)

    def _fix_taskbar(self):
        try:
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW  = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            hwnd  = ctypes.windll.user32.GetParent(self.root.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE,
                                                (style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW)
        except Exception:
            pass

    # ── Construcción ─────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_scanline()
        self._build_metrics()
        self._build_buttons()
        self._build_main_content()
        self._build_resize_handle()

    # ── Header ───────────────────────────────────────────────────────────────

    def _build_header(self):
        hdr   = tk.Frame(self.root, bg=BG); hdr.pack(fill="x")
        inner = tk.Frame(hdr, bg=BG);      inner.pack(fill="x", padx=36, pady=(2,1))
        left  = tk.Frame(inner, bg=BG);    left.pack(side="left")

        self._hex_c = tk.Canvas(left, width=38, height=38, bg=BG, highlightthickness=0)
        self._hex_c.pack(side="left", padx=(0,14))
        self._draw_hex()

        lbl_title = tk.Label(left, text="BOT EJECUCIÓN", bg=BG, fg=WHITE,
                             font=("Segoe UI", 15, "bold"))
        lbl_title.pack(side="left")
        lbl_sub = tk.Label(left, text="  /  MONITOR", bg=BG, fg=DIM2,
                           font=("Segoe UI", 12))
        lbl_sub.pack(side="left")

        ctrl = tk.Frame(inner, bg=BG); ctrl.pack(side="right", padx=(6,0))
        WinBtn(ctrl, "✕", self.root.destroy, RED).pack(side="right", padx=(4,0))
        self._max_btn = WinBtn(ctrl, "□", self._toggle_max, DIM2)
        self._max_btn.pack(side="right", padx=(4,0))
        WinBtn(ctrl, "─", self._minimize_win, YELLOW).pack(side="right", padx=(4,0))

        right = tk.Frame(inner, bg=BG); right.pack(side="right", padx=(0,12))
        self._spinner = Spinner(right, size=22, color=GREEN)
        self._spinner_visible = False
        self._dot = PulseRing(right, size=10, color=DIM2)
        self._dot.pack(side="left", padx=(0,8))
        self.lbl_status = tk.Label(right, text="Bot detenido", bg=BG, fg=DIM2,
                                   font=("Segoe UI", 9))
        self.lbl_status.pack(side="left")

        for w in (hdr, inner, left, lbl_title, lbl_sub, self._hex_c):
            w.bind("<ButtonPress-1>",   self._drag_start)
            w.bind("<B1-Motion>",       self._drag_move)
            w.bind("<Double-Button-1>", lambda e: self._toggle_max())

    def _draw_hex(self):
        c = self._hex_c; c.delete("all"); cx=cy=19; r=16
        t = (math.sin(self._hex_ph)+1)/2
        fill_c = _lerp(GREEN, WHITE, t*0.4); ring_c = _lerp(GREEN, WHITE, t*0.6)
        pts = []
        for i in range(6):
            a = math.pi/2 + i*(math.pi/3) + self._hex_ph*0.15
            pts += [cx+r*math.cos(a), cy+r*math.sin(a)]
        c.create_polygon(pts, fill=_lerp(fill_c,BG,0.55), outline=fill_c, width=1.5)
        c.create_text(cx, cy, text="▶", fill=ring_c, font=("Segoe UI",11,"bold"))
        self._hex_ph += 0.035
        self.root.after(40, self._draw_hex)

    # ── Ventana ──────────────────────────────────────────────────────────────

    def _drag_start(self, ev):
        if self._maximized: return
        self._drag_ox = ev.x_root - self.root.winfo_x()
        self._drag_oy = ev.y_root - self.root.winfo_y()

    def _drag_move(self, ev):
        if self._maximized: return
        self.root.geometry(f"+{ev.x_root-self._drag_ox}+{ev.y_root-self._drag_oy}")

    def _minimize_win(self):
        self.root.overrideredirect(False); self.root.iconify()
        self.root.bind("<Map>", self._on_restore)

    def _on_restore(self, ev):
        self.root.unbind("<Map>"); self.root.after(10, self._restore_chrome)

    def _restore_chrome(self):
        self.root.overrideredirect(True); self.root.after(20, self._fix_taskbar)

    def _toggle_max(self):
        if self._maximized:
            self.root.geometry(self._normal_geo); self._maximized=False
            self._max_btn._sym="□"; self._max_btn._draw()
        else:
            self._normal_geo = self.root.geometry()
            try:
                import ctypes.wintypes; rc=ctypes.wintypes.RECT()
                ctypes.windll.user32.SystemParametersInfoW(48,0,ctypes.byref(rc),0)
                self.root.geometry(f"{rc.right-rc.left}x{rc.bottom-rc.top}+{rc.left}+{rc.top}")
            except Exception:
                sw=self.root.winfo_screenwidth(); sh=self.root.winfo_screenheight()
                self.root.geometry(f"{sw}x{sh}+0+0")
            self._maximized=True; self._max_btn._sym="⊡"; self._max_btn._draw()

    # ── Scanline ─────────────────────────────────────────────────────────────

    def _build_scanline(self):
        sep = tk.Canvas(self.root, height=2, bg=BG, highlightthickness=0)
        sep.pack(fill="x", padx=36, pady=(3,0)); self._sep=sep
        def tick():
            sep.delete("all"); w=sep.winfo_width()
            if w<2: self.root.after(30,tick); return
            self._scan_x=(self._scan_x+0.006)%1.0
            sep.create_line(0,1,w,1,fill=DIM,width=1)
            gx=int(w*self._scan_x); gw=50
            for dx in range(-gw,gw):
                sep.create_line(gx+dx,0,gx+dx,2,fill=_lerp(BG,GREEN,(1-abs(dx)/gw)**2*0.9))
            self.root.after(22,tick)
        self.root.after(150, tick)

    # ── Tarjetas de métricas ──────────────────────────────────────────────────

    def _build_metrics(self):
        row = tk.Frame(self.root, bg=BG)
        row.pack(fill="x", padx=36, pady=(4,3))
        for i in range(6): row.columnconfigure(i, weight=1)

        defs = [
            ("signal",  "SEÑAL",      GREEN,  "última barra",  lambda v: str(v)),
            ("buy_p",   "P(BUY)",     CYAN,   "probabilidad",  lambda v: f"{v*100:.1f}%"),
            ("sell_p",  "P(SELL)",    RED,    "probabilidad",  lambda v: f"{v*100:.1f}%"),
            ("win_rate","WIN RATE",   GREEN,  "ops ganadoras", lambda v: f"{v*100:.1f}%"),
            ("profit",  "PROFIT",     YELLOW, "total USD",     lambda v: f"{v:.2f}"),
            ("trades",  "OPERACIONES",BLUE,   "cerradas",      lambda v: str(int(v))),
        ]
        self._metric_widgets = {}
        for i, (key, title, color, sub, fmt) in enumerate(defs):
            pad_l = 0 if i==0 else 4; pad_r = 0 if i==5 else 4
            card = NeonCard(row, accent=color, auto_height=True)
            card.grid(row=0, column=i, sticky="nsew", padx=(pad_l, pad_r))
            f = card.frame
            tk.Label(f, text=title, bg=BG_C, fg=DIM2, font=("Segoe UI",7,"bold")).pack(pady=(5,0))
            val_lbl = TickerLabel(f, text="—", bg=BG_C, fg=color, font=("Segoe UI",13,"bold"))
            val_lbl.pack()
            tk.Label(f, text=sub, bg=BG_C, fg=DIM, font=("Segoe UI",6)).pack(pady=(0,4))
            self._metric_widgets[key] = {"lbl": val_lbl, "fmt": fmt, "color": color}

    # ── Contenido principal ───────────────────────────────────────────────────

    def _build_main_content(self):
        row = tk.Frame(self.root, bg=BG)
        row.pack(fill="both", expand=True, padx=36, pady=(0,3))

        # ── COLUMNA IZQUIERDA: señal actual + historial ───────────────────────
        left = tk.Frame(row, bg=BG); left.pack(side="left", fill="both", expand=True, padx=(0,6))

        # Señal actual
        sig_card = NeonCard(left, accent=GREEN, auto_height=True)
        sig_card.pack(fill="x")
        fs = sig_card.frame

        hrow = tk.Frame(fs, bg=BG_C); hrow.pack(fill="x", pady=(4,0))
        tk.Label(hrow, text="SEÑAL ACTUAL", bg=BG_C, fg=GREEN,
                 font=("Segoe UI",8,"bold")).pack(side="left")
        self.lbl_bar_time = tk.Label(hrow, text="—", bg=BG_C, fg=DIM2, font=("Segoe UI",7))
        self.lbl_bar_time.pack(side="right")

        self.lbl_big_signal = tk.Label(fs, text="ESPERANDO", bg=BG_C, fg=DIM2,
                                       font=("Segoe UI", 22, "bold"))
        self.lbl_big_signal.pack(pady=(2,0))

        details = tk.Frame(fs, bg=BG_C); details.pack(fill="x", pady=(2,6))
        self.lbl_sig_detail = tk.Label(details, text="—", bg=BG_C, fg=DIM2,
                                       font=("Segoe UI",8), justify="left", anchor="w")
        self.lbl_sig_detail.pack(fill="x", padx=4)

        # Posiciones abiertas
        pos_card = NeonCard(left, accent=ORANGE, auto_height=True)
        pos_card.pack(fill="x", pady=(4,0))
        fp = pos_card.frame
        tk.Label(fp, text="POSICIÓN ABIERTA", bg=BG_C, fg=ORANGE,
                 font=("Segoe UI",8,"bold")).pack(anchor="w", pady=(4,0))
        self.lbl_position = tk.Label(fp, text="Sin posiciones abiertas",
                                     bg=BG_C, fg=DIM2, font=("Segoe UI",9),
                                     justify="left", anchor="w")
        self.lbl_position.pack(anchor="w", pady=(0,6))

        # Historial de trades
        hist_card = NeonCard(left, accent=CYAN)
        hist_card.pack(fill="both", expand=True, pady=(4,0))
        fh = hist_card.frame

        hrow2 = tk.Frame(fh, bg=BG_C); hrow2.pack(fill="x", pady=(4,0))
        tk.Label(hrow2, text="HISTORIAL DE OPERACIONES", bg=BG_C, fg=CYAN,
                 font=("Segoe UI",8,"bold")).pack(side="left")
        self.lbl_hist_count = tk.Label(hrow2, text="", bg=BG_C, fg=DIM2, font=("Segoe UI",7))
        self.lbl_hist_count.pack(side="right")

        self._hist_text = tk.Text(fh, bg=BG_C, fg=TEXT, font=("Consolas",8),
                                  bd=0, highlightthickness=0, state="disabled",
                                  wrap="none", selectbackground=DIM2)
        sb = NeonScrollbar(fh, command=self._hist_text.yview, color=CYAN, bg=BG_C)
        self._hist_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", padx=(0,2))
        self._hist_text.pack(fill="both", expand=True, pady=(2,4))
        self._hist_text.tag_config("win",    foreground=GREEN)
        self._hist_text.tag_config("loss",   foreground=RED)
        self._hist_text.tag_config("header", foreground=DIM2)

        # ── COLUMNA DERECHA: estado del bot + log ─────────────────────────────
        right = tk.Frame(row, bg=BG); right.pack(side="left", fill="both", expand=True)

        # Estado del modelo
        mdl_card = NeonCard(right, accent=PURPLE, auto_height=True)
        mdl_card.pack(fill="x")
        fm = mdl_card.frame
        tk.Label(fm, text="MODELO CARGADO", bg=BG_C, fg=PURPLE,
                 font=("Segoe UI",8,"bold")).pack(anchor="w", pady=(4,0))
        self.lbl_model = tk.Label(fm, text="Sin modelo", bg=BG_C, fg=DIM2,
                                  font=("Segoe UI",8), anchor="w", wraplength=380)
        self.lbl_model.pack(anchor="w", pady=(0,4))

        # Log
        log_card = NeonCard(right, accent=CYAN)
        log_card.pack(fill="both", expand=True, pady=(4,0))
        f3 = log_card.frame
        lhr = tk.Frame(f3, bg=BG_C); lhr.pack(fill="x", pady=(4,0))
        tk.Label(lhr, text="LOG EN TIEMPO REAL", bg=BG_C, fg=CYAN,
                 font=("Segoe UI",8,"bold")).pack(side="left")
        tk.Label(lhr, text="últimas 80 líneas", bg=BG_C, fg=DIM2,
                 font=("Segoe UI",7)).pack(side="right")

        self.log_text = tk.Text(f3, bg=BG_LOG, fg=TEXT, font=("Consolas",8),
                                state="disabled", wrap="none", bd=0,
                                highlightthickness=0, selectbackground=DIM2)
        sb_l   = NeonScrollbar(f3, command=self.log_text.yview, color=CYAN, bg=BG_C)
        sb_l_x = NeonScrollbar(f3, command=self.log_text.xview, color=CYAN, bg=BG_C,
                               orient="horizontal")
        self.log_text.configure(yscrollcommand=sb_l.set, xscrollcommand=sb_l_x.set)
        sb_l.pack(side="right", fill="y", padx=(0,2))
        sb_l_x.pack(side="bottom", fill="x", pady=(0,2))
        self.log_text.pack(fill="both", expand=True, pady=(3,0))
        self.log_text.tag_config("info",    foreground=DIM2)
        self.log_text.tag_config("warning", foreground=YELLOW)
        self.log_text.tag_config("error",   foreground=RED)
        self.log_text.tag_config("success", foreground=GREEN)
        self.log_text.tag_config("buy",     foreground=CYAN)
        self.log_text.tag_config("sell",    foreground=ORANGE)

    # ── Botones ───────────────────────────────────────────────────────────────

    def _build_buttons(self):
        row = tk.Frame(self.root, bg=BG); row.pack(side="bottom", pady=(3,4))

        self.btn_start = NeonButton(row, text="▶  INICIAR BOT",
                                    command=self._start_bot, color=GREEN, fg=BG, bw=160, bh=30)
        self.btn_start.pack(side="left", padx=4)

        self.btn_stop = NeonButton(row, text="⏹  DETENER",
                                   command=self._stop_bot, color=RED, fg=WHITE, bw=130, bh=30)
        self.btn_stop.pack(side="left", padx=4)
        self.btn_stop.set_enabled(False)

        self.btn_once = NeonButton(row, text="⚡  TEST (1 barra)",
                                   command=self._run_once, color=ORANGE, fg=WHITE, bw=160, bh=30)
        self.btn_once.pack(side="left", padx=4)

        NeonButton(row, text="✕  CERRAR",
                   command=self.root.destroy, color=BG_C2, fg=TEXT, bw=108, bh=30
                   ).pack(side="left", padx=4)

    # ── Handle de redimensión ─────────────────────────────────────────────────

    def _build_resize_handle(self):
        rh = tk.Canvas(self.root, width=14, height=14, bg=BG,
                       highlightthickness=0, bd=0, cursor="size_nw_se")
        rh.place(relx=1.0, rely=1.0, anchor="se")
        for off in (3,6,9):
            rh.create_line(off,13,13,off,fill=_lerp(BG,DIM2,0.9),width=1)
        rh.bind("<ButtonPress-1>",  self._resize_start)
        rh.bind("<B1-Motion>",      self._resize_move)

    def _resize_start(self, ev):
        self._rz_ox=ev.x_root; self._rz_oy=ev.y_root
        self._rz_ow=self.root.winfo_width(); self._rz_oh=self.root.winfo_height()

    def _resize_move(self, ev):
        if self._maximized: return
        nw=max(780,self._rz_ow+ev.x_root-self._rz_ox)
        nh=max(560,self._rz_oh+ev.y_root-self._rz_oy)
        self.root.geometry(f"{nw}x{nh}")

    # ── Refresco de datos ─────────────────────────────────────────────────────

    def _refresh(self):
        self._update_state()
        self._update_log()
        self._update_history()
        self._update_model_info()
        self.root.after(REFRESH_MS, self._refresh)

    def _update_state(self):
        """Lee state.json y actualiza métricas y señal."""
        if not STATE_FILE.exists():
            return
        try:
            with open(STATE_FILE, encoding="utf-8") as f:
                s = json.load(f)
        except Exception:
            return

        running = s.get("running", False)
        self._dot.set_color(GREEN if running else DIM2)
        self.lbl_status.config(
            text="Bot activo" if running else "Bot detenido",
            fg=GREEN if running else DIM2,
        )

        # Señal
        signal = s.get("last_signal", "—")
        sig_color = {"BUY": CYAN, "SELL": RED, "HOLD": YELLOW}.get(signal, DIM2)
        self.lbl_big_signal.config(text=signal, fg=sig_color)

        bar_time = s.get("last_bar_time", "—")
        self.lbl_bar_time.config(text=bar_time)

        detail = (
            f"Close: {s.get('last_close','—')}  ·  "
            f"RSI: {s.get('last_rsi','—')}  ·  "
            f"ATR: {s.get('last_atr','—')}  ·  "
            f"Acción: {s.get('last_action','—')}"
        )
        self.lbl_sig_detail.config(text=detail)

        # Posición (simplificada — se obtiene del estado)
        open_pos = s.get("open_positions", 0)
        if open_pos:
            self.lbl_position.config(text=f"{open_pos} posición(es) abierta(s)", fg=ORANGE)
        else:
            self.lbl_position.config(text="Sin posiciones abiertas", fg=DIM2)

        # Métricas
        buy_p  = s.get("buy_prob",   0.0)
        sell_p = s.get("sell_prob",  0.0)
        wr     = s.get("win_rate",   0.0)
        profit = s.get("total_profit", 0.0)
        trades = s.get("total_trades", 0)

        sig_map = {"BUY": 1, "SELL": 2, "HOLD": 0}
        self._metric_widgets["signal"]["lbl"].animate_to(signal, str, sig_color)
        self._metric_widgets["buy_p"]["lbl"].animate_to(
            buy_p, lambda v: f"{v*100:.1f}%", CYAN if buy_p >= 0.35 else DIM2)
        self._metric_widgets["sell_p"]["lbl"].animate_to(
            sell_p, lambda v: f"{v*100:.1f}%", RED if sell_p >= 0.35 else DIM2)
        self._metric_widgets["win_rate"]["lbl"].animate_to(
            wr, lambda v: f"{v*100:.1f}%", GREEN if wr >= 0.52 else YELLOW if wr >= 0.45 else RED)
        self._metric_widgets["profit"]["lbl"].animate_to(
            profit, lambda v: f"{v:.2f}", GREEN if profit >= 0 else RED)
        self._metric_widgets["trades"]["lbl"].animate_to(trades, lambda v: str(int(v)), BLUE)

    def _update_model_info(self):
        """Muestra info del modelo del botentrenamiento."""
        if not MODEL_PATH.exists():
            self.lbl_model.config(text="Sin modelo — ejecuta botentrenamiento primero", fg=RED)
            return
        try:
            import os
            mtime = os.path.getmtime(MODEL_PATH)
            from datetime import datetime
            mod_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            metrics_str = ""
            if METRICS_PATH.exists():
                with open(METRICS_PATH) as f:
                    m = json.load(f)
                metrics_str = (
                    f"  ·  Sharpe: {m.get('sharpe','—')} "
                    f"| WR: {m.get('win_rate',0)*100:.1f}% "
                    f"| DD: {m.get('max_drawdown',0)*100:.1f}%"
                )
            self.lbl_model.config(
                text=f"model_latest.pkl  ·  Guardado: {mod_str}{metrics_str}",
                fg=GREEN,
            )
        except Exception as exc:
            self.lbl_model.config(text=f"Error leyendo modelo: {exc}", fg=RED)

    def _update_history(self):
        """Lee los últimos trades cerrados de la BD."""
        try:
            from execution.tracker import get_recent_trades, get_stats
            trades = get_recent_trades(limit=30)
            stats  = get_stats()
        except Exception:
            return

        total = stats.get("total_trades", 0)
        wins  = stats.get("wins", 0)
        self.lbl_hist_count.config(
            text=f"{total} cerradas  ·  {wins} ganadas",
            fg=CYAN,
        )

        self._hist_text.config(state="normal")
        self._hist_text.delete("1.0", "end")

        if not trades:
            self._hist_text.insert("end", "Sin trades cerrados aún\n", "header")
        else:
            hdr = f"{'DIR':<5}  {'OPEN':>10}  {'CLOSE':>10}  {'PROFIT':>8}  {'PIPS':>6}  CONF\n"
            self._hist_text.insert("end", hdr, "header")
            for t in trades:
                profit = t.get("profit") or 0
                pips   = t.get("pips")   or 0
                tag    = "win" if profit > 0 else "loss"
                icon   = "▲" if profit > 0 else "▼"
                line = (
                    f"{icon} {t.get('direction','?'):<3}  "
                    f"{t.get('open_price',0):>10.5f}  "
                    f"{t.get('close_price',0):>10.5f}  "
                    f"{profit:>+8.2f}  "
                    f"{pips:>+6.1f}  "
                    f"{t.get('confidence',0):.2f}\n"
                )
                self._hist_text.insert("end", line, tag)

        self._hist_text.config(state="disabled")

    def _update_log(self):
        if not LOG_FILE.exists():
            return
        try:
            with open(LOG_FILE, encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            return

        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        for line in lines[-80:]:
            ul = line.upper()
            if "[WARNING]"  in ul: tag = "warning"
            elif "[ERROR]"  in ul or "[CRITICAL]" in ul: tag = "error"
            elif "SEÑAL: BUY" in line or "dir: buy" in line.lower(): tag = "buy"
            elif "SEÑAL: SELL" in line or "dir: sell" in line.lower(): tag = "sell"
            elif "guardado" in line.lower() or "abierta" in line.lower() \
                 or "cerrada" in line.lower(): tag = "success"
            else: tag = "info"
            self.log_text.insert("end", line, tag)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    # ── Acciones de botones ───────────────────────────────────────────────────

    def _is_running(self):
        return self._process and self._process.poll() is None

    def _show_spinner(self):
        if not self._spinner_visible:
            self._spinner.pack(side="left", padx=(0,8), before=self._dot)
            self._spinner_visible = True

    def _hide_spinner(self):
        if self._spinner_visible:
            self._spinner.pack_forget()
            self._spinner_visible = False

    def _start_bot(self):
        if self._is_running():
            return
        self.btn_start.set_enabled(False)
        self.btn_stop.set_enabled(True)
        self.btn_once.set_enabled(False)
        self._show_spinner()
        self.lbl_status.config(text="Iniciando...", fg=YELLOW)
        threading.Thread(
            target=self._worker,
            args=([sys.executable, str(BASE_DIR / "exec_bot.py")],),
            daemon=True,
        ).start()

    def _stop_bot(self):
        if self._process and self._process.poll() is None:
            self._process.terminate()
            self.lbl_status.config(text="Deteniendo...", fg=YELLOW)

    def _run_once(self):
        if self._is_running():
            messagebox.showwarning("Bot activo", "El bot ya está corriendo.")
            return
        self.btn_once.set_enabled(False)
        self.btn_start.set_enabled(False)
        self._show_spinner()
        self.lbl_status.config(text="Ejecutando 1 barra...", fg=YELLOW)
        threading.Thread(
            target=self._worker,
            args=([sys.executable, str(BASE_DIR / "exec_bot.py"), "--once"],),
            daemon=True,
        ).start()

    def _worker(self, cmd):
        self._process = subprocess.Popen(
            cmd, cwd=str(BASE_DIR), creationflags=subprocess.CREATE_NO_WINDOW
        )
        self._process.wait()
        self.root.after(0, self._done)

    def _done(self):
        self.btn_start.set_enabled(True)
        self.btn_stop.set_enabled(False)
        self.btn_once.set_enabled(True)
        self._hide_spinner()
        self._update_state()
        self._update_log()
        self._update_history()


def main():
    root = tk.Tk()
    Dashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
