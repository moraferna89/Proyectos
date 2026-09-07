"""
Dashboard para monitorear el Bot de Entrenamiento.
Ejecutar con: python dashboard.py  (o pythonw dashboard.py para sin consola)
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

# Ocultar la ventana de consola de Windows al abrir con python.exe
try:
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
except Exception:
    pass

BASE_DIR         = Path(__file__).resolve().parent
METRICS_PATH     = BASE_DIR / "models" / "metrics.json"
LAST_RUN_PATH    = BASE_DIR / "models" / "last_run.json"
HISTORY_PATH     = BASE_DIR / "models" / "metrics_history.json"
PROGRESS_PATH    = BASE_DIR / "models" / "optuna_progress.json"
BEST_PARAMS_PATH = BASE_DIR / "models" / "best_params.json"
MODEL_PATH       = BASE_DIR / "models" / "model_latest.pkl"
STUDY_DB_PATH    = BASE_DIR / "models" / "optuna_study.db"
TRIALS_PATH      = BASE_DIR / "models" / "optuna_trials.json"
LOG_PATH         = BASE_DIR / "logs"   / "train_bot.log"

RESET_FILES = [
    MODEL_PATH, METRICS_PATH, LAST_RUN_PATH, HISTORY_PATH,
    PROGRESS_PATH, BEST_PARAMS_PATH, STUDY_DB_PATH, TRIALS_PATH,
]
REFRESH_MS = 3000

# ── Paleta VS Code Dark High Contrast ────────────────────────────────────────
BG     = "#000000"   # negro puro (HC background)
BG_C   = "#0a0a0a"   # fondo de cards (casi negro)
BG_C2  = "#111111"   # fondo secundario
BG_LOG = "#000000"   # fondo del log
TEXT   = "#ffffff"   # blanco puro (HC foreground)
DIM    = "#1a1a1a"   # separadores muy sutiles
DIM2   = "#2d6a7a"   # versión oscurecida del acento para elementos inactivos
CYAN   = "#6fc3df"   # HC contrastBorder — color principal para bordes y líneas
GREEN  = "#23d18b"   # verde HC
RED    = "#f14c4c"   # rojo HC
YELLOW = "#f5f543"   # amarillo HC
BLUE   = "#3794ff"   # azul HC
PURPLE = "#d670d6"   # morado HC
TEAL   = "#6fc3df"   # igual que CYAN en HC
WHITE  = "#ffffff"   # blanco puro
ORANGE = "#e07c3e"   # naranja (botón optimizar)


def _lerp(c1: str, c2: str, t: float) -> str:
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    return (f"#{int(r1+(r2-r1)*t):02x}"
            f"{int(g1+(g2-g1)*t):02x}"
            f"{int(b1+(b2-b1)*t):02x}")


# ─────────────────────────────────────────────────────────────────────────────
#  WIDGET: PulseRing  –  indicador de estado con anillos pulsantes
# ─────────────────────────────────────────────────────────────────────────────
class PulseRing(tk.Canvas):
    RINGS = 3

    def __init__(self, parent, size=12, color=DIM2, **kw):
        kw.setdefault("bg", BG)
        sz = size + 22
        super().__init__(parent, width=sz, height=sz,
                         highlightthickness=0, bd=0, **kw)
        self._size  = size
        self._color = color
        self._phase = [i * (2 * math.pi / self.RINGS) for i in range(self.RINGS)]
        self._alive = True
        self._tick()

    def _tick(self):
        self.delete("all")
        sz = self.winfo_width() or (self._size + 22)
        cx = cy = sz // 2
        r  = self._size // 2
        for i in range(self.RINGS):
            self._phase[i] += 0.08
            t  = (math.sin(self._phase[i]) + 1) / 2
            rr = r + 3 + int(t * 8)
            c  = _lerp(BG, self._color, (1 - t) * 0.55)
            self.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                             fill="", outline=c, width=1)
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         fill=self._color, outline="")
        self.create_oval(cx - r // 2, cy - r // 2,
                         cx + r // 2, cy + r // 2,
                         fill=_lerp(self._color, WHITE, 0.45), outline="")
        if self._alive:
            self.after(35, self._tick)

    def set_color(self, c):
        self._color = c

    def destroy(self):
        self._alive = False
        super().destroy()


# ─────────────────────────────────────────────────────────────────────────────
#  WIDGET: NeonCard  –  card con borde neón animado
# ─────────────────────────────────────────────────────────────────────────────
class NeonCard(tk.Canvas):
    INSET = 8

    def __init__(self, parent, accent=CYAN, auto_height=False, **kw):
        kw.setdefault("bg", BG)
        super().__init__(parent, highlightthickness=0, bd=0, **kw)
        self._accent    = accent
        self._auto_h    = auto_height
        self._phase     = 0.0
        self._alive     = True
        self._last_fh   = 0

        self._frame = tk.Frame(self, bg=BG_C)
        self._wid   = self.create_window(
            self.INSET, self.INSET, anchor="nw", window=self._frame
        )
        self.bind("<Configure>", self._on_cfg)
        if self._auto_h:
            self._frame.bind("<Configure>", self._sync_h)
        self._glow_tick()

    def _sync_h(self, ev):
        """En modo auto, el canvas sigue la altura del frame."""
        if abs(ev.height - self._last_fh) < 2:
            return
        self._last_fh = ev.height
        self.configure(height=ev.height + 2 * self.INSET)

    def _on_cfg(self, ev):
        iw = max(4, ev.width - 2 * self.INSET)
        if self._auto_h:
            # Solo ajusta ancho; la altura la gobierna el frame
            self.itemconfig(self._wid, width=iw)
        else:
            ih = max(4, ev.height - 2 * self.INSET)
            self.itemconfig(self._wid, width=iw, height=ih)
        self._draw(ev.width, ev.height)

    def _draw(self, w=None, h=None):
        self.delete("brd")
        w = w or self.winfo_width()
        h = h or self.winfo_height()
        if w < 10 or h < 10:
            return
        t  = (math.sin(self._phase) + 1) / 2
        gi = 0.22 + t * 0.48

        # Background
        self.create_rectangle(0, 0, w, h, fill=BG_C, outline="", tags="brd")

        # Glow border — 3 layers
        for off, alpha in ((2, 0.18), (1, 0.80), (0, 0.42)):
            c = _lerp(BG, self._accent, gi * alpha)
            self.create_rectangle(off, off, w - off, h - off,
                                  fill="", outline=c, width=1, tags="brd")

        # Accent line at top (bright, short)
        bright = _lerp(BG_C, self._accent, gi * 0.95)
        self.create_line(10, 1, w - 10, 1, fill=bright, width=2, tags="brd")

        # Small corner brackets (sz=8)
        sz = 8
        cc = _lerp(BG, self._accent, min(1.0, gi * 1.4))
        for x, y, dx, dy in [
            (0, 0, sz, 0), (0, 0, 0, sz),
            (w, 0, -sz, 0), (w, 0, 0, sz),
            (0, h, sz, 0), (0, h, 0, -sz),
            (w, h, -sz, 0), (w, h, 0, -sz),
        ]:
            self.create_line(x, y, x + dx, y + dy,
                             fill=cc, width=2, tags="brd")

    def _glow_tick(self):
        if not self._alive:
            return
        self._phase += 0.045
        self._draw()
        self.after(45, self._glow_tick)

    def set_accent(self, c):
        self._accent = c

    @property
    def frame(self):
        return self._frame

    def destroy(self):
        self._alive = False
        super().destroy()


# ─────────────────────────────────────────────────────────────────────────────
#  WIDGET: TickerLabel  –  número que anima hacia el nuevo valor
# ─────────────────────────────────────────────────────────────────────────────
class TickerLabel(tk.Label):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._cur  = 0.0
        self._tgt  = 0.0
        self._fmt  = lambda v: f"{v:.3f}"
        self._anim = False
        self._job  = None

    def animate_to(self, value, fmt_fn, color=None):
        if color:
            self.config(fg=color)
        if not isinstance(value, (int, float)):
            self._anim = False
            self.config(text=str(value))
            return
        self._tgt = float(value)
        self._fmt = fmt_fn
        if not self._anim:
            self._step()

    def _step(self):
        diff = self._tgt - self._cur
        if abs(diff) < max(abs(self._tgt) * 0.003, 0.00005):
            self._cur  = self._tgt
            self._anim = False
            try:
                self.config(text=self._fmt(self._cur))
            except Exception:
                pass
            return
        self._anim = True
        self._cur += diff * 0.14
        try:
            self.config(text=self._fmt(self._cur))
        except Exception:
            pass
        self._job = self.after(16, self._step)


# ─────────────────────────────────────────────────────────────────────────────
#  WIDGET: ShimmerBar  –  barra de progreso con barrido de brillo
# ─────────────────────────────────────────────────────────────────────────────
class ShimmerBar(tk.Canvas):
    def __init__(self, parent, height=8, color=CYAN, track=BG_C2, **kw):
        kw["bg"] = BG_C
        super().__init__(parent, height=height,
                         highlightthickness=0, bd=0, **kw)
        self._color    = color
        self._track    = track
        self._h        = height
        self._progress = 0.0
        self._target   = 0.0
        self._shimmer  = 0.0
        self._alive    = True
        self.bind("<Configure>", lambda e: self._draw())
        self._shimmer_tick()

    def set_progress(self, value, animate=True):
        self._target = max(0.0, min(1.0, value))
        if not animate:
            self._progress = self._target
        else:
            self._ease()

    def _ease(self):
        diff = self._target - self._progress
        if abs(diff) < 0.003:
            self._progress = self._target
            self._draw()
            return
        self._progress += diff * 0.16
        self._draw()
        self.after(16, self._ease)

    def _shimmer_tick(self):
        if not self._alive:
            return
        self._shimmer = (self._shimmer + 0.014) % 1.0
        self._draw()
        self.after(18, self._shimmer_tick)

    def _draw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self._h
        if w < 4:
            return
        r = h // 2
        self._rr(0, 0, w, h, r, fill=self._track, outline="")
        fw = int(w * self._progress)
        if fw > r * 2:
            self._rr(0, 0, fw, h, r, fill=self._color, outline="")
            sw = max(18, fw // 3)
            sx = int((fw - sw) * self._shimmer)
            sc = _lerp(self._color, WHITE, 0.50)
            self.create_rectangle(sx, 1, sx + sw, h - 1,
                                  fill=sc, outline="", stipple="gray50")
        pct = int(self._progress * 100)
        self.create_text(w // 2, h // 2, text=f"{pct}%",
                         fill=_lerp(self._color, WHITE, 0.65),
                         font=("Segoe UI", 6, "bold"), anchor="center")

    def _rr(self, x1, y1, x2, y2, r, **kw):
        pts = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
               x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
               x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        self.create_polygon(pts, smooth=True, **kw)

    def destroy(self):
        self._alive = False
        super().destroy()


# ─────────────────────────────────────────────────────────────────────────────
#  WIDGET: NeonButton  –  botón con barrido luminoso en hover
# ─────────────────────────────────────────────────────────────────────────────
class NeonButton(tk.Canvas):
    def __init__(self, parent, text, command,
                 color=BLUE, fg=WHITE, bw=160, bh=40, radius=7, **kw):
        kw["bg"] = BG
        super().__init__(parent, width=bw, height=bh,
                         highlightthickness=0, bd=0, cursor="hand2", **kw)
        self._text    = text
        self._cmd     = command
        self._color   = color
        self._fg      = fg
        self._radius  = radius
        self._bw      = bw
        self._bh      = bh
        self._enabled = True
        self._hover   = False
        self._pressed = False
        self._sweep   = -0.3
        self._sweeping = False
        self._alive   = True
        self._phase   = 0.0

        self.bind("<Enter>",           self._on_enter)
        self.bind("<Leave>",           self._on_leave)
        self.bind("<Button-1>",        self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self._draw()

    def _draw(self):
        self.delete("all")
        w, h, r = self._bw, self._bh, self._radius

        if not self._enabled:
            fill = _lerp(self._color, BG, 0.78)
            tc   = _lerp(self._fg, BG, 0.65)
            border = _lerp(self._color, BG, 0.60)
        elif self._pressed:
            fill   = _lerp(self._color, "#000000", 0.25)
            tc     = self._fg
            border = self._color
        elif self._hover:
            fill   = _lerp(self._color, WHITE, 0.12)
            tc     = self._fg
            border = _lerp(self._color, WHITE, 0.5)
        else:
            fill   = self._color
            tc     = self._fg
            border = _lerp(self._color, WHITE, 0.3)

        pts = [r, 0, w-r, 0, w, 0, w, r,
               w, h-r, w, h, w-r, h, r, h,
               0, h, 0, h-r, 0, r, 0, 0]
        self.create_polygon(pts, smooth=True, fill=fill, outline="")

        # Sweep band
        if self._hover and self._enabled and not self._pressed:
            sw = w // 3
            sx = int((w + sw * 1.6) * self._sweep - sw // 2)
            band = _lerp(fill, WHITE, 0.28)
            self.create_rectangle(sx, 0, sx + sw, h, fill=band, outline="")

        # Top shine
        if self._enabled and not self._pressed:
            sh = _lerp(fill, WHITE, 0.15)
            self.create_rectangle(r, 0, w - r, h // 3, fill=sh, outline="")

        # Glow border
        if self._hover and self._enabled:
            self.create_polygon(pts, smooth=True, fill="", outline=border, width=1)

        self.create_text(w // 2, h // 2, text=self._text,
                         fill=tc, font=("Segoe UI", 9, "bold"), anchor="center")

    def _start_sweep(self):
        self._sweep    = -0.3
        self._sweeping = True
        self._do_sweep()

    def _do_sweep(self):
        if not self._hover or not self._alive:
            self._sweeping = False
            return
        self._sweep += 0.042
        self._draw()
        if self._sweep < 1.35:
            self.after(14, self._do_sweep)
        else:
            self._sweeping = False

    def _on_enter(self, _):
        if self._enabled:
            self._hover = True
            if not self._sweeping:
                self._start_sweep()

    def _on_leave(self, _):
        self._hover   = False
        self._pressed = False
        self._draw()

    def _on_press(self, _):
        if self._enabled:
            self._pressed = True
            self._draw()

    def _on_release(self, _):
        if self._enabled and self._pressed:
            self._pressed = False
            self._hover   = True
            self._draw()
            self._cmd()

    def set_enabled(self, v):
        self._enabled = v
        self._hover   = False
        self._pressed = False
        self._draw()

    def set_text(self, t):
        self._text = t
        self._draw()

    def set_color(self, c):
        self._color = c
        self._draw()

    def destroy(self):
        self._alive = False
        super().destroy()


# ─────────────────────────────────────────────────────────────────────────────
#  WIDGET: NeonScrollbar  –  scrollbar integrado al diseño
# ─────────────────────────────────────────────────────────────────────────────
class NeonScrollbar(tk.Canvas):
    W       = 8
    THUMB   = 4
    THUMB_H = 6

    def __init__(self, parent, command=None, color=DIM2, bg=BG_C,
                 orient="vertical", **kw):
        self._orient = orient
        if orient == "horizontal":
            super().__init__(parent, height=self.W, bg=bg,
                             highlightthickness=0, bd=0, cursor="arrow", **kw)
        else:
            super().__init__(parent, width=self.W, bg=bg,
                             highlightthickness=0, bd=0, cursor="arrow", **kw)
        self._cmd    = command
        self._color  = color
        self._bg     = bg
        self._f0     = 0.0
        self._f1     = 1.0
        self._hover  = False
        self._drag_p = None
        self._drag_f = None

        self.bind("<Configure>",       lambda e: self._draw())
        self.bind("<Enter>",           self._on_enter)
        self.bind("<Leave>",           self._on_leave)
        self.bind("<ButtonPress-1>",   self._on_press)
        self.bind("<B1-Motion>",       self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<MouseWheel>",      self._on_wheel)

    def set(self, first, last):
        self._f0 = float(first)
        self._f1 = float(last)
        self._draw()

    def _draw(self):
        self.delete("all")
        cw = self.winfo_width()  or 200
        ch = self.winfo_height() or self.W
        track_c = _lerp(self._bg, WHITE, 0.04)

        if self._orient == "horizontal":
            if cw < 4:
                return
            my = ch // 2
            self.create_line(4, my, cw - 4, my, fill=track_c, width=1)
            if self._f1 - self._f0 >= 0.999:
                return
            th  = self.THUMB_H if self._hover else self.THUMB
            ty0 = (ch - th) // 2
            ty1 = ty0 + th
            tx0 = max(4,      int(cw * self._f0) + 2)
            tx1 = min(cw - 4, max(tx0 + 20, int(cw * self._f1) - 2))
            tc  = _lerp(self._color, WHITE, 0.35 if self._hover else 0.0)
            self._pill(tx0, ty0, tx1, ty1, th // 2, fill=tc, outline="")
        else:
            if ch < 4:
                return
            mx = cw // 2
            self.create_line(mx, 4, mx, ch - 4, fill=track_c, width=1)
            if self._f1 - self._f0 >= 0.999:
                return
            tw  = self.THUMB_H if self._hover else self.THUMB
            tx0 = (cw - tw) // 2
            tx1 = tx0 + tw
            ty0 = max(4,      int(ch * self._f0) + 2)
            ty1 = min(ch - 4, max(ty0 + 20, int(ch * self._f1) - 2))
            tc  = _lerp(self._color, WHITE, 0.35 if self._hover else 0.0)
            self._pill(tx0, ty0, tx1, ty1, tw // 2, fill=tc, outline="")

    def _pill(self, x1, y1, x2, y2, r, **kw):
        r = min(r, (x2 - x1) // 2, max(1, (y2 - y1) // 2))
        pts = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
               x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
               x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        self.create_polygon(pts, smooth=True, **kw)

    def _on_enter(self, _):
        self._hover = True
        self._draw()

    def _on_leave(self, _):
        self._hover = False
        self._draw()

    def _on_press(self, ev):
        if self._orient == "horizontal":
            cs  = self.winfo_width()
            pos = ev.x
        else:
            cs  = self.winfo_height()
            pos = ev.y
        p0 = int(cs * self._f0)
        p1 = int(cs * self._f1)
        if p0 <= pos <= p1:
            self._drag_p = pos
            self._drag_f = self._f0
        else:
            if self._cmd:
                self._cmd("moveto", pos / cs - (self._f1 - self._f0) / 2)

    def _on_drag(self, ev):
        if self._drag_p is None or self._cmd is None:
            return
        if self._orient == "horizontal":
            cs  = self.winfo_width()
            pos = ev.x
        else:
            cs  = self.winfo_height()
            pos = ev.y
        diff = (pos - self._drag_p) / cs
        self._cmd("moveto", self._drag_f + diff)

    def _on_release(self, _):
        self._drag_p = None
        self._drag_f = None

    def _on_wheel(self, ev):
        if self._cmd:
            self._cmd("scroll", -1 if ev.delta > 0 else 1, "units")


# ─────────────────────────────────────────────────────────────────────────────
#  WIDGET: Spinner  –  rueda giratoria para estado de carga
# ─────────────────────────────────────────────────────────────────────────────
class Spinner(tk.Canvas):
    def __init__(self, parent, size=20, color=YELLOW, **kw):
        kw.setdefault("bg", BG)
        super().__init__(parent, width=size, height=size,
                         highlightthickness=0, bd=0, **kw)
        self._size  = size
        self._color = color
        self._angle = 0.0
        self._alive = True
        self._tick()

    def _tick(self):
        self.delete("all")
        cx = cy = self._size // 2
        r  = cx - 2
        segs = 10
        for i in range(segs):
            a1 = math.radians(self._angle + i * (360 / segs))
            a2 = a1 + math.radians(360 / segs * 0.65)
            t  = i / segs
            c  = _lerp(BG, self._color, t ** 0.6)
            self.create_arc(cx - r, cy - r, cx + r, cy + r,
                            start=math.degrees(a1),
                            extent=math.degrees(a2 - a1),
                            style="arc", outline=c, width=3)
        self._angle = (self._angle + 8) % 360
        if self._alive:
            self.after(28, self._tick)

    def set_color(self, c):
        self._color = c

    def destroy(self):
        self._alive = False
        super().destroy()


# ─────────────────────────────────────────────────────────────────────────────
#  WIDGET: WinBtn  –  botones de control de ventana (min/max/cerrar)
# ─────────────────────────────────────────────────────────────────────────────
class WinBtn(tk.Canvas):
    SIZE = 13

    def __init__(self, parent, symbol, command, hover_color, **kw):
        kw.setdefault("bg", BG)
        super().__init__(parent, width=self.SIZE, height=self.SIZE,
                         highlightthickness=0, bd=0, cursor="hand2", **kw)
        self._sym = symbol
        self._cmd = command
        self._hc  = hover_color
        self._hov = False
        self.bind("<Enter>",           lambda e: self._hover(True))
        self.bind("<Leave>",           lambda e: self._hover(False))
        self.bind("<ButtonRelease-1>", lambda e: self._cmd())
        self._draw()

    def _hover(self, v):
        self._hov = v
        self._draw()

    def _draw(self):
        self.delete("all")
        sz = self.SIZE
        if self._hov:
            self.create_oval(0, 0, sz, sz, fill=self._hc, outline="")
            self.create_text(sz // 2, sz // 2, text=self._sym,
                             fill=WHITE, font=("Segoe UI", 6, "bold"), anchor="center")
        else:
            self.create_oval(1, 1, sz - 1, sz - 1,
                             fill=_lerp(BG, DIM2, 0.7), outline="")


# ─────────────────────────────────────────────────────────────────────────────
#  DASHBOARD PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
class Dashboard:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Bot Entrenamiento — Monitor")
        self.root.configure(bg=BG)
        self.root.overrideredirect(True)

        self._process    = None
        self._scan_x     = 0.0
        self._hex_ph     = 0.0
        self._maximized  = False
        self._normal_geo = None
        self._drag_ox    = 0
        self._drag_oy    = 0
        self._rz_ox      = 0
        self._rz_oy      = 0
        self._rz_ow      = 0
        self._rz_oh      = 0

        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        w  = max(860, min(1120, int(sw * 0.82)))
        h  = max(620, min(int(sh * 0.88), sh - 60))
        x  = (sw - w) // 2
        y  = (sh - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")
        root.minsize(780, 560)

        self._build_ui()
        self._refresh()
        # Aplicar después del primer render para que el HWND exista
        root.after(100, self._fix_taskbar)

    # ── Registrar ventana en la barra de tareas y Alt+Tab ──────────────────────

    def _fix_taskbar(self):
        """overrideredirect quita WS_EX_APPWINDOW; lo restauramos via ctypes."""
        try:
            import ctypes
            GWL_EXSTYLE      = -20
            WS_EX_APPWINDOW  = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            hwnd  = ctypes.windll.user32.GetParent(self.root.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = (style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        except Exception:
            pass

    # ── Construcción ──────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_scanline()
        self._build_metrics()
        self._build_buttons()       # primero reclama espacio desde abajo
        self._build_main_content()  # luego llena el espacio restante
        self._build_resize_handle()

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill="x", padx=0, pady=0)

        inner = tk.Frame(hdr, bg=BG)
        inner.pack(fill="x", padx=36, pady=(2, 1))

        left = tk.Frame(inner, bg=BG)
        left.pack(side="left")

        # Hexágono animado
        self._hex_c = tk.Canvas(left, width=38, height=38,
                                bg=BG, highlightthickness=0)
        self._hex_c.pack(side="left", padx=(0, 14))
        self._draw_hex()

        lbl_title = tk.Label(left, text="BOT ENTRENAMIENTO", bg=BG, fg=WHITE,
                 font=("Segoe UI", 15, "bold"))
        lbl_title.pack(side="left")
        lbl_sub = tk.Label(left, text="  /  MONITOR", bg=BG, fg=DIM2,
                 font=("Segoe UI", 12))
        lbl_sub.pack(side="left")

        # ── Controles de ventana (esquina superior derecha) ───────────────────
        ctrl = tk.Frame(inner, bg=BG)
        ctrl.pack(side="right", padx=(6, 0))

        WinBtn(ctrl, "✕", self.root.destroy,   RED).pack(side="right", padx=(4, 0))
        self._max_btn = WinBtn(ctrl, "□", self._toggle_max,   DIM2)
        self._max_btn.pack(side="right", padx=(4, 0))
        WinBtn(ctrl, "─", self._minimize_win,  YELLOW).pack(side="right", padx=(4, 0))

        # ── Estado y spinner ──────────────────────────────────────────────────
        right = tk.Frame(inner, bg=BG)
        right.pack(side="right", padx=(0, 12))

        self._spinner = Spinner(right, size=22, color=YELLOW)
        self._spinner_visible = False

        self._dot = PulseRing(right, size=10, color=DIM2)
        self._dot.pack(side="left", padx=(0, 8))

        self.lbl_status = tk.Label(right, text="Sin datos aún",
                                   bg=BG, fg=DIM2, font=("Segoe UI", 9))
        self.lbl_status.pack(side="left")

        # ── Arrastre de ventana (bindings en toda el área del header) ─────────
        for widget in (hdr, inner, left, lbl_title, lbl_sub, self._hex_c):
            widget.bind("<ButtonPress-1>",   self._drag_start)
            widget.bind("<B1-Motion>",       self._drag_move)
            widget.bind("<Double-Button-1>", lambda e: self._toggle_max())

    def _draw_hex(self):
        c = self._hex_c
        c.delete("all")
        cx, cy = 19, 19
        r = 16
        t = (math.sin(self._hex_ph) + 1) / 2
        fill_c  = _lerp(CYAN, WHITE, t * 0.4)
        ring_c  = _lerp(CYAN, WHITE, t * 0.6)
        pts = []
        for i in range(6):
            a = math.pi / 2 + i * (math.pi / 3) + self._hex_ph * 0.15
            pts += [cx + r * math.cos(a), cy + r * math.sin(a)]
        c.create_polygon(pts, fill=_lerp(fill_c, BG, 0.55),
                         outline=fill_c, width=1.5)
        c.create_text(cx, cy, text="⚙", fill=ring_c,
                      font=("Segoe UI", 11, "bold"))
        self._hex_ph += 0.035
        self.root.after(40, self._draw_hex)

    # ── Controles de ventana ─────────────────────────────────────────────────

    def _drag_start(self, ev):
        if self._maximized:
            return
        self._drag_ox = ev.x_root - self.root.winfo_x()
        self._drag_oy = ev.y_root - self.root.winfo_y()

    def _drag_move(self, ev):
        if self._maximized:
            return
        x = ev.x_root - self._drag_ox
        y = ev.y_root - self._drag_oy
        self.root.geometry(f"+{x}+{y}")

    def _minimize_win(self):
        self.root.overrideredirect(False)
        self.root.iconify()
        self.root.bind("<Map>", self._on_restore)

    def _on_restore(self, ev):
        self.root.unbind("<Map>")
        self.root.after(10, self._restore_chrome)

    def _restore_chrome(self):
        self.root.overrideredirect(True)
        self.root.after(20, self._fix_taskbar)

    def _toggle_max(self):
        if self._maximized:
            self.root.geometry(self._normal_geo)
            self._maximized = False
            self._max_btn._sym = "□"
            self._max_btn._draw()
        else:
            self._normal_geo = self.root.geometry()
            try:
                import ctypes, ctypes.wintypes
                rc = ctypes.wintypes.RECT()
                ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rc), 0)
                ww = rc.right - rc.left
                wh = rc.bottom - rc.top
                self.root.geometry(f"{ww}x{wh}+{rc.left}+{rc.top}")
            except Exception:
                sw = self.root.winfo_screenwidth()
                sh = self.root.winfo_screenheight()
                self.root.geometry(f"{sw}x{sh}+0+0")
            self._maximized = True
            self._max_btn._sym = "⊡"
            self._max_btn._draw()

    # ── Scanline  (punto de luz que recorre el separador) ─────────────────────

    def _build_scanline(self):
        sep = tk.Canvas(self.root, height=2, bg=BG, highlightthickness=0)
        sep.pack(fill="x", padx=36, pady=(3, 0))
        self._sep = sep

        def tick():
            sep.delete("all")
            w = sep.winfo_width()
            if w < 2:
                self.root.after(30, tick)
                return
            self._scan_x = (self._scan_x + 0.006) % 1.0
            sep.create_line(0, 1, w, 1, fill=DIM, width=1)
            gx = int(w * self._scan_x)
            gw = 50
            for dx in range(-gw, gw):
                t = 1 - abs(dx) / gw
                col = _lerp(BG, CYAN, t ** 2 * 0.9)
                sep.create_line(gx + dx, 0, gx + dx, 2, fill=col)
            self.root.after(22, tick)

        self.root.after(150, tick)

    # ── Tarjetas de métricas ──────────────────────────────────────────────────

    def _build_metrics(self):
        row = tk.Frame(self.root, bg=BG)
        row.pack(fill="x", padx=36, pady=(4, 3))
        for i in range(5):
            row.columnconfigure(i, weight=1)

        defs = [
            ("sharpe", "SHARPE",      CYAN,   "riesgo ajustado",    lambda v: f"{v:.3f}"),
            ("wr",     "WIN RATE",    GREEN,  "ops ganadoras",      lambda v: f"{v*100:.1f}%"),
            ("dd",     "DRAWDOWN",    RED,    "desde pico",         lambda v: f"{v*100:.1f}%"),
            ("pf",     "PROF. FACTOR",YELLOW, "ganancia/pérdida",   lambda v: f"{v:.2f}"),
            ("trades", "OPERACIONES", BLUE,   "total",              lambda v: str(int(v))),
        ]
        self._metrics = {}
        for i, (key, title, color, sub, fmt) in enumerate(defs):
            pad_l = 0 if i == 0 else 4
            pad_r = 0 if i == 4 else 4
            card = NeonCard(row, accent=color, auto_height=True)
            card.grid(row=0, column=i, sticky="nsew", padx=(pad_l, pad_r))

            f = card.frame
            tk.Label(f, text=title, bg=BG_C, fg=DIM2,
                     font=("Segoe UI", 7, "bold")).pack(pady=(5, 0))
            val_lbl = TickerLabel(f, text="—", bg=BG_C, fg=color,
                                  font=("Segoe UI", 13, "bold"))
            val_lbl.pack(pady=(0, 0))
            tk.Label(f, text=sub, bg=BG_C, fg=DIM,
                     font=("Segoe UI", 6)).pack(pady=(0, 4))

            self._metrics[key] = {"lbl": val_lbl, "fmt": fmt}

    # ── Contenido principal: dos columnas ────────────────────────────────────

    def _build_main_content(self):
        row = tk.Frame(self.root, bg=BG)
        row.pack(fill="both", expand=True, padx=36, pady=(0, 3))

        # ════════════════════════════════════════════════════════════════════
        # COLUMNA IZQUIERDA: Optuna + Trials + Historial
        # ════════════════════════════════════════════════════════════════════
        left = tk.Frame(row, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))

        # ── Optuna ────────────────────────────────────────────────────────
        opt = NeonCard(left, accent=CYAN, auto_height=True)
        opt.pack(fill="x")
        f = opt.frame

        hr = tk.Frame(f, bg=BG_C)
        hr.pack(fill="x", pady=(3, 0))
        tk.Label(hr, text="OPTIMIZACIÓN  /  OPTUNA", bg=BG_C, fg=CYAN,
                 font=("Segoe UI", 8, "bold")).pack(side="left")
        self.lbl_opt_status = tk.Label(hr, text="Sin ejecutar",
                                       bg=BG_C, fg=DIM2, font=("Segoe UI", 7))
        self.lbl_opt_status.pack(side="right")

        self.opt_bar = ShimmerBar(f, height=2, color=CYAN)
        self.opt_bar.pack(fill="x", pady=(2, 1))

        self.lbl_opt_progress = tk.Label(f, text="", bg=BG_C, fg=CYAN,
                                         font=("Segoe UI", 7), anchor="w")
        self.lbl_opt_progress.pack(fill="x")

        self.lbl_opt_params = tk.Label(f, text="", bg=BG_C, fg=DIM2,
                                       font=("Segoe UI", 7), anchor="w",
                                       justify="left", wraplength=800)
        self.lbl_opt_params.pack(fill="x", pady=(0, 3))

        # ── Trials ────────────────────────────────────────────────────────
        tc = NeonCard(left, accent=CYAN)
        tc.pack(fill="both", expand=True, pady=(3, 0))
        ft = tc.frame

        thr = tk.Frame(ft, bg=BG_C)
        thr.pack(fill="x", pady=(3, 0))
        tk.Label(thr, text="RESULTADOS TRIALS — OPTUNA",
                 bg=BG_C, fg=CYAN, font=("Segoe UI", 8, "bold")).pack(side="left")
        self.lbl_trials_summary = tk.Label(
            thr, text="Sin datos", bg=BG_C, fg=DIM2, font=("Segoe UI", 7))
        self.lbl_trials_summary.pack(side="right")

        ti = tk.Frame(ft, bg=BG_C)
        ti.pack(fill="both", expand=True, pady=(2, 3))
        self._trials_text = tk.Text(
            ti, bg=BG_C, fg=TEXT, font=("Consolas", 8),
            bd=0, highlightthickness=0,
            state="disabled", wrap="none",
            selectbackground=DIM2, insertbackground=TEXT,
        )
        sb_t   = NeonScrollbar(ti, command=self._trials_text.yview, color=CYAN, bg=BG_C)
        sb_t_x = NeonScrollbar(ti, command=self._trials_text.xview, color=CYAN, bg=BG_C,
                               orient="horizontal")
        self._trials_text.configure(yscrollcommand=sb_t.set, xscrollcommand=sb_t_x.set)
        sb_t.pack(side="right", fill="y", padx=(0, 2))
        sb_t_x.pack(side="bottom", fill="x", pady=(0, 2))
        self._trials_text.pack(fill="both", expand=True)
        self._trials_text.tag_config("pass",  foreground=GREEN)
        self._trials_text.tag_config("fail",  foreground=RED)
        self._trials_text.tag_config("best",  foreground=YELLOW)

        # ── Historial ─────────────────────────────────────────────────────
        hist = NeonCard(left, accent=CYAN)
        hist.pack(fill="both", expand=True, pady=(3, 0))
        fh = hist.frame

        tk.Label(fh, text="HISTORIAL  —  MODELOS GUARDADOS",
                 bg=BG_C, fg=CYAN, font=("Segoe UI", 8, "bold")).pack(
                     anchor="w", pady=(4, 2))

        self._hist_text = tk.Text(
            fh, bg=BG_C, fg=TEXT, font=("Consolas", 8),
            bd=0, highlightthickness=0, state="disabled",
            wrap="none", selectbackground=DIM2, insertbackground=TEXT,
        )
        sb_h   = NeonScrollbar(fh, command=self._hist_text.yview, color=CYAN, bg=BG_C)
        sb_h_x = NeonScrollbar(fh, command=self._hist_text.xview, color=CYAN, bg=BG_C,
                               orient="horizontal")
        self._hist_text.configure(yscrollcommand=sb_h.set, xscrollcommand=sb_h_x.set)
        sb_h.pack(side="right", fill="y", padx=(0, 2))
        sb_h_x.pack(side="bottom", fill="x", pady=(0, 2))
        self._hist_text.pack(fill="both", expand=True)
        self._hist_text.tag_config("saved",   foreground=GREEN)
        self._hist_text.tag_config("unsaved", foreground=YELLOW)
        self._hist_text.tag_config("trial",   foreground=CYAN)
        self._hist_text.tag_config("params",  foreground=DIM2)

        # ════════════════════════════════════════════════════════════════════
        # COLUMNA DERECHA: Último entrenamiento + Log
        # ════════════════════════════════════════════════════════════════════
        right = tk.Frame(row, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        # ── Último entrenamiento ──────────────────────────────────────────
        lr = NeonCard(right, accent=CYAN, auto_height=True)
        lr.pack(fill="x")
        f2 = lr.frame

        tk.Label(f2, text="ÚLTIMO ENTRENAMIENTO", bg=BG_C, fg=CYAN,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(4, 2))
        self.lbl_lastrun = tk.Label(f2, text="Sin datos aún",
                                    bg=BG_C, fg=DIM2, font=("Segoe UI", 8),
                                    anchor="w", justify="left", wraplength=380)
        self.lbl_lastrun.pack(anchor="w", pady=(0, 4))

        # ── Log ───────────────────────────────────────────────────────────
        log_card = NeonCard(right, accent=CYAN)
        log_card.pack(fill="both", expand=True, pady=(3, 0))
        f3 = log_card.frame

        lhr = tk.Frame(f3, bg=BG_C)
        lhr.pack(fill="x", pady=(4, 0))
        tk.Label(lhr, text="LOG EN TIEMPO REAL",
                 bg=BG_C, fg=CYAN, font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Label(lhr, text="últimas 60 líneas",
                 bg=BG_C, fg=DIM2, font=("Segoe UI", 7)).pack(side="right")

        self.log_text = tk.Text(
            f3, bg=BG_LOG, fg=TEXT,
            font=("Consolas", 8), state="disabled",
            wrap="none", bd=0, highlightthickness=0,
            selectbackground=DIM2, insertbackground=TEXT,
        )
        sb_l   = NeonScrollbar(f3, command=self.log_text.yview, color=CYAN, bg=BG_C)
        sb_l_x = NeonScrollbar(f3, command=self.log_text.xview, color=CYAN, bg=BG_C,
                               orient="horizontal")
        self.log_text.configure(yscrollcommand=sb_l.set, xscrollcommand=sb_l_x.set)
        sb_l.pack(side="right", fill="y", padx=(0, 2))
        sb_l_x.pack(side="bottom", fill="x", pady=(0, 2))
        self.log_text.pack(fill="both", expand=True, pady=(3, 0))
        self.log_text.tag_config("info",    foreground=DIM2)
        self.log_text.tag_config("warning", foreground=YELLOW)
        self.log_text.tag_config("error",   foreground=RED)
        self.log_text.tag_config("success", foreground=GREEN)
        self.log_text.tag_config("optuna",  foreground=PURPLE)

    # ── Botones ───────────────────────────────────────────────────────────────

    def _build_buttons(self):
        row = tk.Frame(self.root, bg=BG)
        row.pack(side="bottom", pady=(3, 4))

        self.btn_optimize = NeonButton(
            row, text="◈  OPTIMIZAR + ENTRENAR",
            command=self._run_optimize,
            color=ORANGE, fg=WHITE, bw=220, bh=30,
        )
        self.btn_optimize.pack(side="left", padx=4)

        self.btn_train = NeonButton(
            row, text="▶  ENTRENAR",
            command=self._run_training,
            color=GREEN, fg=BG, bw=144, bh=30,
        )
        self.btn_train.pack(side="left", padx=4)

        self.btn_reset = NeonButton(
            row, text="⚠  RESET",
            command=self._reset_all,
            color=RED, fg=WHITE, bw=108, bh=30,
        )
        self.btn_reset.pack(side="left", padx=4)

        NeonButton(
            row, text="✕  CERRAR",
            command=self.root.destroy,
            color=BG_C2, fg=TEXT, bw=108, bh=30,
        ).pack(side="left", padx=4)


    # ── Handle de redimensión (esquina inferior derecha) ──────────────────────

    def _build_resize_handle(self):
        rh = tk.Canvas(self.root, width=14, height=14, bg=BG,
                       highlightthickness=0, bd=0, cursor="size_nw_se")
        rh.place(relx=1.0, rely=1.0, anchor="se")
        for off in (3, 6, 9):
            rh.create_line(off, 13, 13, off, fill=_lerp(BG, DIM2, 0.9), width=1)
        rh.bind("<ButtonPress-1>",  self._resize_start)
        rh.bind("<B1-Motion>",      self._resize_move)

    def _resize_start(self, ev):
        self._rz_ox = ev.x_root
        self._rz_oy = ev.y_root
        self._rz_ow = self.root.winfo_width()
        self._rz_oh = self.root.winfo_height()

    def _resize_move(self, ev):
        if self._maximized:
            return
        nw = max(780, self._rz_ow + ev.x_root - self._rz_ox)
        nh = max(560, self._rz_oh + ev.y_root - self._rz_oy)
        self.root.geometry(f"{nw}x{nh}")

    # ── Refresco de datos ─────────────────────────────────────────────────────

    def _refresh(self):
        self._update_metrics()
        self._update_lastrun()
        self._update_history()
        self._update_optimization()
        self._update_trials()
        self._update_log()
        self.root.after(REFRESH_MS, self._refresh)

    def _update_metrics(self):
        m, label_at, color_at = None, "", DIM2

        if METRICS_PATH.exists():
            try:
                with open(METRICS_PATH) as f:
                    m = json.load(f)
                label_at = "Modelo activo guardado"
                color_at = GREEN
            except Exception:
                pass

        if m is None and HISTORY_PATH.exists():
            try:
                with open(HISTORY_PATH) as f:
                    hist = json.load(f)
                if hist:
                    m = max(hist, key=lambda h: h.get("sharpe", -999))
                    label_at = "Mejor en historial"
                    color_at = BLUE
            except Exception:
                pass

        if m is None and LAST_RUN_PATH.exists():
            try:
                with open(LAST_RUN_PATH) as f:
                    m = json.load(f)
                label_at = "Último entrenamiento"
                color_at = YELLOW
            except Exception:
                pass

        if m is None:
            self.lbl_status.config(text="Sin datos aún", fg=DIM2)
            self._dot.set_color(DIM2)
            return

        sharpe = m.get("sharpe", 0)
        wr     = m.get("win_rate", 0)
        dd     = m.get("max_drawdown", 0)
        pf     = m.get("profit_factor", 0)
        trades = m.get("n_trades", 0)
        date   = m.get("saved_at", m.get("run_at", ""))

        sharpe_c = GREEN  if sharpe >= 1.0 else YELLOW if sharpe >= 0.5 else RED
        wr_c     = GREEN  if wr     >= 0.5 else YELLOW if wr     >= 0.45 else RED
        dd_c     = GREEN  if dd     <= 0.10 else YELLOW if dd    <= 0.15 else RED
        pf_c     = GREEN  if pf     >= 1.5  else YELLOW if pf    >= 1.0  else RED

        self._metrics["sharpe"]["lbl"].animate_to(
            sharpe, self._metrics["sharpe"]["fmt"], sharpe_c)
        self._metrics["wr"]["lbl"].animate_to(
            wr, self._metrics["wr"]["fmt"], wr_c)
        self._metrics["dd"]["lbl"].animate_to(
            dd, self._metrics["dd"]["fmt"], dd_c)
        self._metrics["pf"]["lbl"].animate_to(
            pf, self._metrics["pf"]["fmt"], pf_c)
        self._metrics["trades"]["lbl"].animate_to(
            trades, self._metrics["trades"]["fmt"], CYAN)

        self.lbl_status.config(text=f"{label_at}  ·  {date}", fg=color_at)
        self._dot.set_color(color_at)

    def _update_lastrun(self):
        if not LAST_RUN_PATH.exists():
            return
        try:
            with open(LAST_RUN_PATH) as f:
                m = json.load(f)
        except Exception:
            return
        sharpe    = m.get("sharpe", 0)
        wf_sharpe = m.get("wf_sharpe", 0)
        wr        = m.get("win_rate", 0)
        dd        = m.get("max_drawdown", 0)
        pf        = m.get("profit_factor", 0)
        run_at    = m.get("run_at", "")
        saved     = m.get("model_saved", False)
        reason    = m.get("reason", "")
        icon  = "✓" if saved else "✗"
        color = GREEN if saved else YELLOW
        text  = (f"Sharpe OOS: {sharpe:.3f}  ·  WF: {wf_sharpe:.3f}\n"
                 f"WR: {wr*100:.1f}%  ·  DD: {dd*100:.1f}%  ·  PF: {pf:.2f}\n"
                 f"{run_at}\n{icon}  {reason}")
        self.lbl_lastrun.config(text=text, fg=color)

    def _update_history(self):
        if not HISTORY_PATH.exists():
            self._hist_write("Sin historial aún")
            return
        try:
            with open(HISTORY_PATH) as f:
                history = json.load(f)
        except Exception:
            return
        if not history:
            self._hist_write("Sin historial aún")
            return

        self._hist_text.config(state="normal")
        self._hist_text.delete("1.0", "end")
        for i, h in enumerate(history[-8:], 1):
            s      = h.get("sharpe", 0)
            saved  = h.get("model_saved", False)
            source = h.get("source", "training")
            if source == "trial":
                tag  = "trial"
                tnum = h.get("trial_number", "?")
                icon = f"◈ T#{tnum}"
            elif saved:
                tag  = "saved"
                icon = "✓"
            else:
                tag  = "unsaved"
                icon = "✗"
            arrow = "▲" if s >= 1.0 else "~" if s >= 0.5 else "▼"
            date  = h.get("saved_at", h.get("run_at", ""))
            p     = h.get("params", {})
            line1 = (
                f"{icon} #{i}  Sharpe: {s:.3f} {arrow}  "
                f"WR: {h.get('win_rate',0)*100:.1f}%  "
                f"DD: {h.get('max_drawdown',0)*100:.1f}%  "
                f"PF: {h.get('profit_factor',0):.2f}  [{date}]\n"
            )
            self._hist_text.insert("end", line1, tag)
            if p:
                line2 = (
                    f"   {p.get('SYMBOL','?')} {p.get('TIMEFRAME','?')}  "
                    f"H={p.get('LABEL_HORIZON','?')}  "
                    f"THRESH={p.get('LABEL_THRESHOLD','?')}  "
                    f"RSI={p.get('RSI_PERIOD','?')}  "
                    f"EMA={p.get('EMA_FAST','?')}/{p.get('EMA_SLOW','?')}  "
                    f"depth={p.get('max_depth','?')}  "
                    f"lr={round(p.get('learning_rate', 0), 4)}\n\n"
                )
                self._hist_text.insert("end", line2, "params")
        self._hist_text.config(state="disabled")

    def _hist_write(self, msg):
        self._hist_text.config(state="normal")
        self._hist_text.delete("1.0", "end")
        self._hist_text.insert("end", msg, "params")
        self._hist_text.config(state="disabled")

    def _update_optimization(self):
        if not PROGRESS_PATH.exists():
            return
        try:
            with open(PROGRESS_PATH) as f:
                p = json.load(f)
        except Exception:
            return
        current = p.get("current_trial", 0)
        total   = p.get("total_trials", 1)
        best    = p.get("best_sharpe", 0)
        status  = p.get("status", "")
        params  = p.get("best_params", {})
        updated = p.get("updated_at", "")
        pct     = current / total if total else 0

        self.opt_bar.set_progress(pct)

        if status == "running":
            self.lbl_opt_status.config(text=f"⏳ {updated}", fg=YELLOW)
        elif status == "completed":
            self.lbl_opt_status.config(text=f"✓ Completado  {updated}", fg=GREEN)
        else:
            self.lbl_opt_status.config(text="Sin ejecutar", fg=DIM2)

        self.lbl_opt_progress.config(
            text=f"{current}/{total} trials  ·  Mejor Sharpe: {best:.4f}"
        )
        if params:
            kp = "  ·  ".join([
                f"H={params.get('LABEL_HORIZON','—')}",
                f"THRESH={params.get('LABEL_THRESHOLD','—')}",
                f"RSI={params.get('RSI_PERIOD','—')}",
                f"EMA={params.get('EMA_FAST','—')}/{params.get('EMA_SLOW','—')}",
                f"depth={params.get('max_depth','—')}",
                f"lr={round(params.get('learning_rate', 0), 4)}",
            ])
            self.lbl_opt_params.config(text=f"Params:  {kp}", fg=DIM2)

    def _update_trials(self):
        if not TRIALS_PATH.exists():
            return
        try:
            with open(TRIALS_PATH) as f:
                trials = json.load(f)
        except Exception:
            return
        if not trials:
            return

        total   = len(trials)
        passing = sum(1 for t in trials if t.get("passes"))
        best    = max((t.get("sharpe", 0) for t in trials), default=0)
        self.lbl_trials_summary.config(
            text=f"{total} trials  ·  {passing} pasan  ·  Mejor Sharpe: {best:.4f}",
            fg=CYAN,
        )

        self._trials_text.config(state="normal")
        self._trials_text.delete("1.0", "end")

        # Mostrar los últimos 40 trials, más reciente arriba
        for t in reversed(trials[-40:]):
            num      = t.get("trial", "?")
            sharpe   = t.get("sharpe", 0)
            n_samp   = t.get("n_samples", 0)
            passes   = t.get("passes", False)
            params   = t.get("params", {})
            ts       = t.get("timestamp", "")
            icon     = "✓" if passes else "✗"
            tag      = "pass" if passes else "fail"

            # Si es el mejor trial, destacarlo
            if abs(sharpe - best) < 1e-6 and best > 0:
                tag = "best"
                icon = "★"

            p_str = (
                f"EMA:{params.get('EMA_FAST','?')}/{params.get('EMA_SLOW','?')}  "
                f"RSI:{params.get('RSI_PERIOD','?')}  "
                f"H:{params.get('LABEL_HORIZON','?')}  "
                f"THR:{params.get('LABEL_THRESHOLD', 0):.5f}  "
                f"depth:{params.get('max_depth','?')}"
            )

            line = (f"#{num:<3}  {icon}  Sharpe:{sharpe:>7.4f}  "
                    f"Muestras:{n_samp:>7,}  {p_str}  [{ts}]\n")
            self._trials_text.insert("end", line, tag)

        self._trials_text.config(state="disabled")

    def _update_log(self):
        if not LOG_PATH.exists():
            return
        try:
            with open(LOG_PATH, encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            return
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        for line in lines[-60:]:
            if "[WARNING]" in line:
                tag = "warning"
            elif "[ERROR]" in line or "[CRITICAL]" in line:
                tag = "error"
            elif "guardado" in line.lower() or "supera" in line.lower():
                tag = "success"
            elif "trial" in line.lower() or "optuna" in line.lower() \
                    or "optimiz" in line.lower():
                tag = "optuna"
            else:
                tag = "info"
            self.log_text.insert("end", line, tag)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _is_running(self):
        return self._process and self._process.poll() is None

    def _show_spinner(self):
        if not self._spinner_visible:
            self._spinner.pack(side="left", padx=(0, 8), before=self._dot)
            self._spinner_visible = True

    def _hide_spinner(self):
        if self._spinner_visible:
            self._spinner.pack_forget()
            self._spinner_visible = False

    def _lock_buttons(self):
        self.btn_train.set_enabled(False)
        self.btn_optimize.set_enabled(False)
        self.btn_reset.set_enabled(False)
        self._show_spinner()

    def _unlock_buttons(self):
        self.btn_train.set_enabled(True)
        self.btn_train.set_text("▶  ENTRENAR")
        self.btn_train.set_color(GREEN)
        self.btn_optimize.set_enabled(True)
        self.btn_optimize.set_text("◈  OPTIMIZAR + ENTRENAR")
        self.btn_optimize.set_color(ORANGE)
        self.btn_reset.set_enabled(True)
        self._hide_spinner()

    def _reset_all(self):
        if self._is_running():
            messagebox.showwarning(
                "Proceso activo",
                "Hay un entrenamiento en curso. Detenlo antes de resetear.")
            return
        if not messagebox.askyesno(
            "Confirmar reset",
            "Esto borrará el modelo, historial, métricas y el estudio Optuna."
            "\n\n¿Continuar?",
            icon="warning",
        ):
            return
        deleted = []
        for p in RESET_FILES:
            if p.exists():
                p.unlink()
                deleted.append(p.name)
        for card in self._metrics.values():
            card["lbl"].config(text="—")
        self.lbl_status.config(text="Sin datos aún", fg=DIM2)
        self._dot.set_color(DIM2)
        self.lbl_lastrun.config(text="Sin datos aún", fg=DIM2)
        self.lbl_opt_status.config(text="Sin ejecutar", fg=DIM2)
        self.lbl_opt_progress.config(text="")
        self.lbl_opt_params.config(text="")
        self.opt_bar.set_progress(0, animate=False)
        self._hist_write("Sin historial aún")
        msg = "Reset completo." if deleted else "No había archivos que borrar."
        self.lbl_status.config(text=msg, fg=DIM2)

    def _run_training(self):
        if self._is_running():
            return
        self.btn_train.set_text("⏳ ENTRENANDO...")
        self.btn_train.set_color(YELLOW)
        self._spinner.set_color(YELLOW)
        self.lbl_status.config(text="Entrenando...", fg=YELLOW)
        self._dot.set_color(YELLOW)
        self._lock_buttons()
        threading.Thread(
            target=self._worker,
            args=([sys.executable, str(BASE_DIR / "train_bot.py")],),
            daemon=True,
        ).start()

    def _run_optimize(self):
        if self._is_running():
            return
        self.btn_optimize.set_text("⏳ OPTIMIZANDO...")
        self.btn_optimize.set_color(YELLOW)
        self._spinner.set_color(ORANGE)
        self.lbl_status.config(text="Buscando mejores parámetros...", fg=ORANGE)
        self._dot.set_color(ORANGE)
        self._lock_buttons()
        threading.Thread(
            target=self._worker,
            args=([sys.executable, str(BASE_DIR / "train_bot.py"), "--optimize"],),
            daemon=True,
        ).start()

    def _worker(self, cmd):
        self._process = subprocess.Popen(
            cmd, cwd=str(BASE_DIR),
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        self._process.wait()
        self.root.after(0, self._done)

    def _done(self):
        self._unlock_buttons()
        self._update_metrics()
        self._update_lastrun()
        self._update_history()
        self._update_optimization()
        self._update_log()


def main():
    root = tk.Tk()
    Dashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
