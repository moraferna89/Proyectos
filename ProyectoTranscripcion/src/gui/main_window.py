import os
import math
import random

from src.gui.inspector import Inspector

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QSizePolicy,
    QApplication, QSizeGrip, QGraphicsOpacityEffect, QFrame
)
from PyQt5.QtCore import (
    Qt, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QTimer, QRectF, QPointF, pyqtProperty
)
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush,
    QPainterPath, QConicalGradient, QLinearGradient, QRadialGradient
)

# ── Palette ────────────────────────────────────────────────────────────────────
BG      = "#050810"
CARD    = "#0D1120"
ACCENT  = "#7C3AED"
ACCENT2 = "#8B5CF6"
ACCENT3 = "#A78BFA"
CYAN    = "#22D3EE"
SUCCESS = "#34D399"
TEXT    = "#F1F5F9"
TEXT_S  = "#94A3B8"
TEXT_M  = "#475569"
BORDER  = "#1E2235"


# ══════════════════════════════════════════════════════════════════════════════
#  BACKGROUND LAYER  –  animated floating orbs
# ══════════════════════════════════════════════════════════════════════════════
class BackgroundLayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._t = 0.0
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(20)

    def _tick(self):
        self._t += 0.007
        self.update()

    def paintEvent(self, _e):
        p = QPainter(self)
        w, h = self.width(), self.height()

        # solid base
        p.fillRect(self.rect(), QColor(5, 8, 16))

        # orb 1 – violet, drifts top-left
        ox1 = w * 0.18 + math.sin(self._t * 0.7)  * w * 0.07
        oy1 = h * 0.28 + math.cos(self._t * 0.53) * h * 0.06
        g1  = QRadialGradient(QPointF(ox1, oy1), min(w, h) * 0.55)
        g1.setColorAt(0.0, QColor(124, 58,  237, 38))
        g1.setColorAt(0.5, QColor(124, 58,  237, 12))
        g1.setColorAt(1.0, QColor(124, 58,  237,  0))
        p.fillRect(self.rect(), QBrush(g1))

        # orb 2 – cyan, drifts bottom-right
        ox2 = w * 0.80 + math.cos(self._t * 0.6)  * w * 0.07
        oy2 = h * 0.70 + math.sin(self._t * 0.81) * h * 0.07
        g2  = QRadialGradient(QPointF(ox2, oy2), min(w, h) * 0.45)
        g2.setColorAt(0.0, QColor(34, 211, 238, 30))
        g2.setColorAt(0.5, QColor(34, 211, 238, 10))
        g2.setColorAt(1.0, QColor(34, 211, 238,  0))
        p.fillRect(self.rect(), QBrush(g2))

        # orb 3 – pink, top-center, subtle
        ox3 = w * 0.55 + math.sin(self._t * 1.1 + 1.0) * w * 0.05
        oy3 = h * 0.07 + math.cos(self._t * 0.9)        * h * 0.03
        g3  = QRadialGradient(QPointF(ox3, oy3), min(w, h) * 0.25)
        g3.setColorAt(0.0, QColor(244, 114, 182, 22))
        g3.setColorAt(1.0, QColor(244, 114, 182,  0))
        p.fillRect(self.rect(), QBrush(g3))


# ══════════════════════════════════════════════════════════════════════════════
#  EQUALIZER BARS
# ══════════════════════════════════════════════════════════════════════════════
class EqBars(QWidget):
    def __init__(self, n=9, parent=None):
        super().__init__(parent)
        self._n       = n
        self._vals    = [random.uniform(0.2, 1.0) for _ in range(n)]
        self._targets = [random.uniform(0.2, 1.0) for _ in range(n)]
        self._active  = True
        self.setFixedSize(n * 14, 40)
        self.setStyleSheet("background: transparent;")
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(80)

    def _tick(self):
        if not self._active:
            return
        for i in range(self._n):
            d = self._targets[i] - self._vals[i]
            self._vals[i] += d * 0.28
            if abs(d) < 0.02:
                self._targets[i] = random.uniform(0.15, 1.0)
        self.update()

    def set_active(self, on: bool):
        self._active = on
        if not on:
            for i in range(self._n):
                self._targets[i] = 0.12

    def paintEvent(self, _e):
        p   = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        bw   = w / (self._n * 2 - 1)

        for i, v in enumerate(self._vals):
            bh = max(4.0, v * h * 0.85)
            x  = i * bw * 2
            y  = (h - bh) / 2

            g = QLinearGradient(0, y, 0, y + bh)
            g.setColorAt(0.0, QColor(167, 139, 250, 220))
            g.setColorAt(1.0, QColor(124, 58,  237, 180))

            path = QPainterPath()
            r    = min(bw / 2, 3.0)
            path.addRoundedRect(QRectF(x, y, bw, bh), r, r)
            p.fillPath(path, QBrush(g))


# ══════════════════════════════════════════════════════════════════════════════
#  RIPPLE BUTTON
# ══════════════════════════════════════════════════════════════════════════════
class RippleButton(QPushButton):
    def __init__(self, text="", parent=None, variant="primary"):
        super().__init__(text, parent)
        self._variant  = variant
        self._hp       = 0.0
        self._ripples  = []   # [x, y, radius, alpha]
        self._pulse_t  = 0.0

        self._hanim = QPropertyAnimation(self, b"hoverProg")
        self._hanim.setDuration(200)
        self._hanim.setEasingCurve(QEasingCurve.OutCubic)

        rt = QTimer(self)
        rt.timeout.connect(self._ripple_tick)
        rt.start(16)

        pt = QTimer(self)
        pt.timeout.connect(self._pulse_tick)
        pt.start(30)

        self.setCursor(Qt.PointingHandCursor)

    # ── animated property ──────────────────────────────────────────────────
    @pyqtProperty(float)
    def hoverProg(self):
        return self._hp

    @hoverProg.setter
    def hoverProg(self, v):
        self._hp = v
        self.update()

    # ── event handlers ────────────────────────────────────────────────────
    def enterEvent(self, _e):
        self._hanim.stop()
        self._hanim.setStartValue(self._hp)
        self._hanim.setEndValue(1.0)
        self._hanim.start()
        super().enterEvent(_e)

    def leaveEvent(self, _e):
        self._hanim.stop()
        self._hanim.setStartValue(self._hp)
        self._hanim.setEndValue(0.0)
        self._hanim.start()
        super().leaveEvent(_e)

    def mousePressEvent(self, e):
        self._ripples.append([float(e.x()), float(e.y()), 0.0, 160])
        super().mousePressEvent(e)

    # ── timers ────────────────────────────────────────────────────────────
    def _ripple_tick(self):
        new = [[x, y, r + 4, a - 7] for x, y, r, a in self._ripples if a > 0]
        if len(new) != len(self._ripples):
            self._ripples = new
            self.update()
        elif new:
            self._ripples = new
            self.update()

    def _pulse_tick(self):
        if self.isEnabled() and self._hp < 0.05:
            self._pulse_t = (self._pulse_t + 0.045) % (2 * math.pi)
            self.update()

    # ── painting ──────────────────────────────────────────────────────────
    def paintEvent(self, _e):
        p    = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect())
        rad  = 14.0
        path = QPainterPath()
        path.addRoundedRect(rect, rad, rad)

        if not self.isEnabled():
            p.fillPath(path, QColor(18, 22, 40))
            p.setPen(QColor(TEXT_M))
            p.setFont(self.font())
            p.drawText(rect, Qt.AlignCenter, self.text())
            return

        if self._variant == "primary":
            pulse = (math.sin(self._pulse_t) + 1) / 2

            # outer glow
            ga = int(22 + 35 * self._hp + 12 * pulse)
            glow = QRadialGradient(rect.center(), rect.width() * 0.8)
            glow.setColorAt(0.3, QColor(124, 58, 237, ga))
            glow.setColorAt(1.0, QColor(124, 58, 237,  0))
            gp = QPainterPath()
            gp.addRoundedRect(rect.adjusted(-8, -8, 8, 8), rad + 6, rad + 6)
            p.fillPath(gp, QBrush(glow))

            # body gradient
            g = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            r1 = QColor(144 + int(20 * self._hp), 70,  250)
            r2 = QColor(124 + int(16 * self._hp), 58,  237)
            g.setColorAt(0.0, r1)
            g.setColorAt(1.0, r2)
            p.fillPath(path, QBrush(g))

            # top-edge shimmer
            sh = QLinearGradient(rect.topLeft(), QPointF(rect.left(), rect.top() + rect.height() * 0.45))
            sh.setColorAt(0.0, QColor(255, 255, 255, int(28 + 18 * self._hp)))
            sh.setColorAt(1.0, QColor(255, 255, 255, 0))
            sp = QPainterPath()
            sp.addRoundedRect(rect.adjusted(1, 1, -1, -1), rad - 1, rad - 1)
            p.fillPath(sp, QBrush(sh))

        elif self._variant == "ghost":
            p.fillPath(path, QColor(124, 58, 237, int(18 * self._hp)))
            bp = QPainterPath()
            bp.addRoundedRect(rect.adjusted(0.75, 0.75, -0.75, -0.75), rad, rad)
            p.setPen(QPen(QColor(139, 92, 246, int(105 + 150 * self._hp)), 1.5))
            p.drawPath(bp)

        # ripple effects (clipped to button shape)
        p.setClipPath(path)
        for rx, ry, rr, ra in self._ripples:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 255, 255, int(ra)))
            p.drawEllipse(QPointF(rx, ry), rr, rr)
        p.setClipping(False)

        # label
        p.setPen(QColor(TEXT) if self._variant == "primary" else QColor(ACCENT3))
        p.setFont(self.font())
        p.drawText(rect, Qt.AlignCenter, self.text())


# ══════════════════════════════════════════════════════════════════════════════
#  PARTICLE  (simple struct)
# ══════════════════════════════════════════════════════════════════════════════
class _Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "size", "r", "g", "b")

    def __init__(self, cx, cy):
        angle    = random.uniform(0, 2 * math.pi)
        speed    = random.uniform(1.5, 7.0)
        self.x   = cx;  self.y  = cy
        self.vx  = speed * math.cos(angle)
        self.vy  = speed * math.sin(angle)
        self.life = 1.0
        self.size = random.uniform(3, 7)
        self.r, self.g, self.b = random.choice([
            (139, 92,  246),
            (34,  211, 238),
            (52,  211, 153),
            (167, 139, 250),
            (244, 114, 182),
        ])


# ══════════════════════════════════════════════════════════════════════════════
#  DROP ZONE  –  orbit rings + eq bars + particles
# ══════════════════════════════════════════════════════════════════════════════
class DropZone(QWidget):
    archivo_elegido = pyqtSignal(str)
    FORMATOS = ('.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(280)
        self.setStyleSheet("background: transparent;")

        self._state          = "idle"
        self._pre_drag_state = "idle"
        self._t              = 0.0
        self._done_alpha     = 0.0    # 0→1 eased transition to done state
        self._particles: list[_Particle] = []

        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(16)

        self._build()

    # ── tick ───────────────────────────────────────────────────────────────
    def _tick(self):
        self._t += 0.018

        # particles
        self._particles = [
            p for p in self._particles if p.life > 0
        ]
        for p in self._particles:
            p.x   += p.vx
            p.y   += p.vy
            p.vy  += 0.14
            p.life -= 0.024

        # ease done_alpha toward target
        target         = 1.0 if self._state == "done" else 0.0
        self._done_alpha += (target - self._done_alpha) * 0.07

        self.update()

    # ── burst ──────────────────────────────────────────────────────────────
    def _burst(self):
        cx, cy = self.width() / 2, self.height() / 2
        for _ in range(40):
            self._particles.append(_Particle(cx, cy))

    # ── layout ─────────────────────────────────────────────────────────────
    def _build(self):
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        lay.setContentsMargins(48, 44, 48, 44)
        lay.setSpacing(14)

        # equalizer
        self.eq = EqBars(9)
        ew = QWidget(); ew.setStyleSheet("background: transparent;")
        el = QHBoxLayout(ew); el.setContentsMargins(0,0,0,0); el.addWidget(self.eq)
        lay.addWidget(ew, alignment=Qt.AlignHCenter)

        self.lbl_title = QLabel("Arrastra tu audio aquí")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet(
            f"color: {TEXT}; font-size: 20px; font-weight: 800; background: transparent;"
        )
        lay.addWidget(self.lbl_title)

        self.lbl_sub = QLabel("MP3  ·  WAV  ·  M4A  ·  OGG  ·  FLAC  ·  AAC")
        self.lbl_sub.setAlignment(Qt.AlignCenter)
        self.lbl_sub.setStyleSheet(
            f"color: {TEXT_M}; font-size: 11px; letter-spacing: 2px; background: transparent;"
        )
        lay.addWidget(self.lbl_sub)

        sep = QLabel("─── o ───")
        sep.setAlignment(Qt.AlignCenter)
        sep.setStyleSheet(f"color: {BORDER}; font-size: 10px; background: transparent;")
        lay.addWidget(sep)

        self.btn_sel = RippleButton("  Seleccionar archivo", variant="ghost")
        self.btn_sel.setFixedSize(192, 40)
        self.btn_sel.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.btn_sel.clicked.connect(self.abrir_dialogo)

        wrap = QWidget(); wrap.setStyleSheet("background: transparent;")
        wr = QHBoxLayout(wrap); wr.setContentsMargins(0,0,0,0)
        wr.addWidget(self.btn_sel)
        lay.addWidget(wrap, alignment=Qt.AlignHCenter)

    # ── painting ───────────────────────────────────────────────────────────
    def paintEvent(self, _e):
        p    = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        rect   = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        radius = 24.0
        cx     = rect.center().x()
        cy     = rect.center().y()
        da     = self._done_alpha

        # ─ card background ──────────────────────────────────────────────
        bg = QPainterPath()
        bg.addRoundedRect(rect, radius, radius)

        bg_col = QColor(
            int(10 + 16 * da),
            int(14 + 28 * da),
            int(24 - 4  * da),
            210
        )
        p.fillPath(bg, bg_col)

        # ─ orbit rings  (fade out as "done" fades in) ───────────────────
        fade = 1.0 - da
        if fade > 0.01:
            rings = [
                (min(cx, cy) * 0.48,  0.90, 0.70, 78),
                (min(cx, cy) * 0.63, -0.62, 0.52, 52),
                (min(cx, cy) * 0.80,  0.42, 0.36, 32),
            ]
            for ring_r, speed, dot_sc, base_a in rings:
                a = int(base_a * fade)
                # ring circle
                p.setPen(QPen(QColor(139, 92, 246, a), 1.2))
                p.setBrush(Qt.NoBrush)
                p.drawEllipse(QPointF(cx, cy), ring_r, ring_r)

                # orbiting dot + glow
                ang  = self._t * speed
                dx   = cx + ring_r * math.cos(ang)
                dy   = cy + ring_r * math.sin(ang)
                da2  = int((a + 80) * fade)
                dr   = 3.5 * dot_sc

                glow = QRadialGradient(QPointF(dx, dy), dr * 3.5)
                glow.setColorAt(0.0, QColor(167, 139, 250, min(255, da2)))
                glow.setColorAt(1.0, QColor(139,  92, 246, 0))
                p.setPen(Qt.NoPen)
                p.setBrush(QBrush(glow))
                p.drawEllipse(QPointF(dx, dy), dr * 3.5, dr * 3.5)

                p.setBrush(QColor(220, 200, 255, min(255, da2 + 70)))
                p.drawEllipse(QPointF(dx, dy), dr, dr)

        # ─ done-state inner glow ────────────────────────────────────────
        if da > 0.02:
            dg = QRadialGradient(QPointF(cx, cy), min(cx, cy) * 0.65)
            dg.setColorAt(0.0, QColor(52, 211, 153, int(32 * da)))
            dg.setColorAt(1.0, QColor(52, 211, 153, 0))
            p.fillPath(bg, QBrush(dg))

        # ─ hover highlight ───────────────────────────────────────────────
        if self._state == "hover":
            p.fillPath(bg, QColor(139, 92, 246, 20))

        # ─ border ring (animated conic gradient) ────────────────────────
        bw    = 1.8
        outer = QPainterPath()
        outer.addRoundedRect(rect, radius, radius)
        inner = QPainterPath()
        inner.addRoundedRect(rect.adjusted(bw, bw, -bw, -bw), radius - 1, radius - 1)
        ring  = outer.subtracted(inner)

        if self._state == "hover":
            p.fillPath(ring, QColor(167, 139, 250, 230))
        elif da > 0.01:
            # blend: conic (fade) → success border
            pulse = (math.sin(self._t * 1.4) + 1) / 2
            a     = int((75 + 50 * pulse) * (1 - da))
            grad  = QConicalGradient(cx, cy, math.degrees(self._t))
            grad.setColorAt(0.00, QColor(139, 92,  246, a + 80))
            grad.setColorAt(0.30, QColor(167, 139, 250, a))
            grad.setColorAt(0.55, QColor(34,  211, 238, a + 40))
            grad.setColorAt(0.80, QColor(167, 139, 250, a))
            grad.setColorAt(1.00, QColor(139, 92,  246, a + 80))
            p.fillPath(ring, QBrush(grad))

            p.fillPath(ring, QColor(52, 211, 153, int(210 * da)))
        else:
            pulse = (math.sin(self._t * 1.4) + 1) / 2
            a     = int(75 + 50 * pulse)
            grad  = QConicalGradient(cx, cy, math.degrees(self._t))
            grad.setColorAt(0.00, QColor(139, 92,  246, a + 80))
            grad.setColorAt(0.30, QColor(167, 139, 250, a))
            grad.setColorAt(0.55, QColor(34,  211, 238, a + 40))
            grad.setColorAt(0.80, QColor(167, 139, 250, a))
            grad.setColorAt(1.00, QColor(139, 92,  246, a + 80))
            p.fillPath(ring, QBrush(grad))

        # ─ particles ────────────────────────────────────────────────────
        p.setPen(Qt.NoPen)
        for pt in self._particles:
            alpha = int(255 * pt.life)
            p.setBrush(QColor(pt.r, pt.g, pt.b, alpha))
            s = pt.size * pt.life
            p.drawEllipse(QPointF(pt.x, pt.y), s, s)

    # ── public API ─────────────────────────────────────────────────────────
    def abrir_dialogo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar audio", "",
            "Archivos de audio (*.mp3 *.wav *.m4a *.ogg *.flac *.aac)"
        )
        if path:
            self.archivo_elegido.emit(path)

    def marcar_listo(self):
        self._state = "done"
        self.lbl_title.setText("¡Archivo cargado!")
        self.lbl_sub.setText("Listo para transcribir")
        self.eq.set_active(False)
        QTimer.singleShot(80, self._burst)

    def resetear(self):
        self._state = "idle"
        self.lbl_title.setText("Arrastra tu audio aquí")
        self.lbl_sub.setText("MP3  ·  WAV  ·  M4A  ·  OGG  ·  FLAC  ·  AAC")
        self.eq.set_active(True)

    # ── drag & drop ────────────────────────────────────────────────────────
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(self.FORMATOS):
                    event.acceptProposedAction()
                    self._pre_drag_state = self._state
                    self._state = "hover"
                    return

    def dragLeaveEvent(self, _e):
        self._state = self._pre_drag_state

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(self.FORMATOS):
                self.archivo_elegido.emit(path)
                break


# ══════════════════════════════════════════════════════════════════════════════
#  FILE CHIP  –  slide-in info card
# ══════════════════════════════════════════════════════════════════════════════
class FileChip(QWidget):
    cambiar_pedido = pyqtSignal()
    _TARGET_H = 66

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self._build()
        self.hide()

        self._anim = QPropertyAnimation(self, b"maximumHeight")
        self._anim.setEasingCurve(QEasingCurve.OutBack)
        self._anim.setDuration(420)

    def _build(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(2, 2, 2, 2)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(13, 17, 32, 0.92);
                border: 1px solid rgba(139, 92, 246, 0.42);
                border-radius: 16px;
            }}
        """)
        cl = QHBoxLayout(card)
        cl.setContentsMargins(14, 10, 14, 10)
        cl.setSpacing(12)

        # icon badge
        badge = QFrame()
        badge.setFixedSize(38, 38)
        badge.setStyleSheet("""
            QFrame {
                background: rgba(124,58,237,0.22);
                border: 1px solid rgba(124,58,237,0.45);
                border-radius: 10px;
            }
        """)
        bl = QHBoxLayout(badge)
        bl.setContentsMargins(0,0,0,0)
        ic = QLabel("🎵")
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet("background: transparent; font-size: 17px;")
        bl.addWidget(ic)
        cl.addWidget(badge)

        col = QVBoxLayout()
        col.setSpacing(1)
        self.lbl_name = QLabel("—")
        self.lbl_name.setStyleSheet(
            f"color: {TEXT}; font-size: 13px; font-weight: 700; background: transparent;"
        )
        self.lbl_size = QLabel("—")
        self.lbl_size.setStyleSheet(
            f"color: {TEXT_M}; font-size: 11px; background: transparent;"
        )
        col.addWidget(self.lbl_name)
        col.addWidget(self.lbl_size)
        cl.addLayout(col)
        cl.addStretch()

        btn = RippleButton("Cambiar", variant="ghost")
        btn.setFixedSize(84, 30)
        btn.setFont(QFont("Segoe UI", 9, QFont.Bold))
        btn.clicked.connect(self.cambiar_pedido.emit)
        cl.addWidget(btn)

        outer.addWidget(card)

    def actualizar(self, path: str):
        name = os.path.basename(path)
        size = os.path.getsize(path)
        mb   = size / (1024 * 1024)
        peso = f"{mb:.1f} MB" if mb >= 1 else f"{size // 1024} KB"
        self.lbl_name.setText(name)
        self.lbl_size.setText(peso)

    def show_animated(self):
        self.setMinimumHeight(0)
        self.setMaximumHeight(0)
        self.show()
        self._anim.stop()
        self._anim.setStartValue(0)
        self._anim.setEndValue(self._TARGET_H)
        self._anim.start()


# ══════════════════════════════════════════════════════════════════════════════
#  TITLE BAR
# ══════════════════════════════════════════════════════════════════════════════
class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent   = parent
        self._drag_pos = None
        self._t        = 0.0
        self.setFixedHeight(50)
        self.setStyleSheet("background: transparent;")
        self._build()

        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(40)

    def _tick(self):
        self._t = (self._t + 0.04) % (2 * math.pi)
        self.update()

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 12, 0)
        lay.setSpacing(8)

        dot = QLabel("◆")
        dot.setStyleSheet(f"color: {ACCENT3}; font-size: 10px; background: transparent;")
        lay.addWidget(dot)

        title = QLabel("Transcriptor de Llamadas")
        title.setStyleSheet(
            f"color: {TEXT}; font-size: 13px; font-weight: 700; "
            f"background: transparent; letter-spacing: 0.3px;"
        )
        lay.addWidget(title)
        lay.addStretch()

        ai = QLabel("AI")
        ai.setStyleSheet(f"""
            color: {ACCENT3};
            background: rgba(124,58,237,0.18);
            border: 1px solid rgba(124,58,237,0.38);
            border-radius: 5px;
            padding: 2px 8px;
            font-size: 9px;
            font-weight: 900;
            letter-spacing: 2px;
        """)
        lay.addWidget(ai)
        lay.addSpacing(10)

        for sym, slot, hbg in [
            ("─", self._parent.showMinimized, "rgba(255,255,255,0.08)"),
            ("□", self._toggle_max,           "rgba(255,255,255,0.08)"),
            ("✕", self._parent.close,         "rgba(239,68,68,0.55)"),
        ]:
            b = QPushButton(sym)
            b.setFixedSize(32, 32)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {TEXT_M};
                    border: none; border-radius: 8px; font-size: 12px;
                }}
                QPushButton:hover {{ background: {hbg}; color: {TEXT}; }}
            """)
            b.clicked.connect(slot)
            lay.addWidget(b)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(5, 8, 16, 195))
        # animated glowing bottom border
        pulse = (math.sin(self._t) + 1) / 2
        p.setPen(QPen(QColor(124, 58, 237, int(35 + 30 * pulse)), 1))
        p.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

    def _toggle_max(self):
        self._parent.showNormal() if self._parent.isMaximized() else self._parent.showMaximized()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPos() - self._parent.pos()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.LeftButton:
            self._parent.move(e.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, _e):
        self._drag_pos = None


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.archivo_actual = None
        self._fade_refs     = None
        self._config()
        self._build_ui()
        self._inspector = Inspector(QApplication.instance(), self)

    def _config(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMinimumSize(740, 580)

        screen = QApplication.primaryScreen().availableGeometry()
        w = max(int(screen.width() * 0.56), 740)
        h = max(int(screen.height() * 0.76), 580)
        self.resize(w, h)
        geo = self.frameGeometry()
        geo.moveCenter(screen.center())
        self.move(geo.topLeft())

    def showEvent(self, event):
        super().showEvent(event)
        if self._fade_refs is None:
            fx   = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(fx)
            anim = QPropertyAnimation(fx, b"opacity")
            anim.setDuration(600)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.start()
            self._fade_refs = (fx, anim)

    def _build_ui(self):
        self._bg = BackgroundLayer()

        rl = QVBoxLayout(self._bg)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        # title bar
        self.title_bar = TitleBar(self)
        rl.addWidget(self.title_bar)

        # body
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(52, 36, 52, 28)
        bl.setSpacing(16)

        h1 = QLabel("Transcripción de Llamadas")
        h1.setStyleSheet(
            f"color: {TEXT}; font-size: 28px; font-weight: 900; "
            f"letter-spacing: -1px; background: transparent;"
        )
        bl.addWidget(h1)

        h2 = QLabel(
            "Sube el audio de una llamada para transcribirlo automáticamente\n"
            "e identificar el desempeño del ejecutivo."
        )
        h2.setStyleSheet(f"color: {TEXT_S}; font-size: 13px; background: transparent;")
        bl.addWidget(h2)

        self.drop_zone = DropZone()
        self.drop_zone.setObjectName("drop_zone")
        self.drop_zone.archivo_elegido.connect(self._on_archivo)
        bl.addWidget(self.drop_zone, stretch=1)

        self.file_chip = FileChip()
        self.file_chip.setObjectName("file_chip")
        self.file_chip.cambiar_pedido.connect(self.drop_zone.abrir_dialogo)
        bl.addWidget(self.file_chip)

        self.btn_main = RippleButton("✦  Transcribir y analizar", variant="primary")
        self.btn_main.setObjectName("btn_transcribir")
        self.btn_main.setFixedHeight(54)
        self.btn_main.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.btn_main.setEnabled(False)
        self.btn_main.clicked.connect(self._on_transcribir)
        bl.addWidget(self.btn_main)

        rl.addWidget(body)

        # resize grip
        gw = QWidget(); gw.setStyleSheet("background: transparent;")
        gr = QHBoxLayout(gw); gr.setContentsMargins(0, 0, 4, 4)
        gr.addStretch()
        grip = QSizeGrip(self); grip.setStyleSheet("background: transparent;")
        gr.addWidget(grip)
        rl.addWidget(gw)

        self.setCentralWidget(self._bg)

    def _on_archivo(self, path: str):
        self.archivo_actual = path
        self.drop_zone.marcar_listo()
        self.file_chip.actualizar(path)
        self.file_chip.show_animated()
        self.btn_main.setEnabled(True)

    def _on_transcribir(self):
        print(f"Transcribiendo: {self.archivo_actual}")
