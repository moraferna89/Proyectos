"""
Inspector de widgets  –  Ctrl+I para activar/desactivar
"""
import math
from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                              QApplication, QShortcut)
from PyQt5.QtCore import QObject, QEvent, Qt, QRectF, QPointF, QTimer, QMetaMethod
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath, QFont, QKeySequence, QCursor


# ══════════════════════════════════════════════════════════════════════════════
#  OVERLAY
# ══════════════════════════════════════════════════════════════════════════════
class _Overlay(QWidget):
    def __init__(self):
        super().__init__(None,
            Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._t = 0.0
        QTimer(self, timeout=self._tick, interval=16).start()
        self.hide()

    def _tick(self):
        if self.isVisible():
            self._t = (self._t + 0.06) % (2 * math.pi)
            self.update()

    def track(self, widget: QWidget):
        pos = widget.mapToGlobal(widget.rect().topLeft())
        self.setGeometry(pos.x()-3, pos.y()-3,
                         widget.width()+6, widget.height()+6)
        self.show()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(1,1,-1,-1)
        bg = QPainterPath()
        bg.addRoundedRect(rect, 5, 5)
        p.fillPath(bg, QColor(124,58,237,22))
        pulse = (math.sin(self._t)+1)/2
        p.setPen(QPen(QColor(167,139,250, int(170+80*pulse)), 2))
        p.drawPath(bg)
        a = int(170+80*pulse)
        for cx,cy in [(rect.left(),rect.top()), (rect.right(),rect.top()),
                      (rect.left(),rect.bottom()), (rect.right(),rect.bottom())]:
            p.fillRect(int(cx)-3, int(cy)-3, 7, 7, QColor(167,139,250,a))


# ══════════════════════════════════════════════════════════════════════════════
#  PANEL  –  hijo directo de la ventana principal (evita problemas de z-order)
# ══════════════════════════════════════════════════════════════════════════════
class _Panel(QWidget):
    _W = 310

    def __init__(self, main_window: QWidget):
        # Padre = main_window + Qt.Tool → siempre encima, sin barra de tarea
        super().__init__(main_window,
            Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(self._W)
        self._build()
        self.hide()
        print("[Inspector] Panel creado, parent =", main_window.__class__.__name__)

    # fondo oscuro pintado a mano (WA_TranslucentBackground sin paintEvent = invisible)
    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()).adjusted(1,1,-1,-1), 12, 12)
        p.fillPath(path, QColor(8, 10, 22, 252))
        p.setPen(QPen(QColor(124, 58, 237, 170), 1.5))
        p.drawPath(path)

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 14)
        lay.setSpacing(3)

        hdr = QHBoxLayout()
        self._cls = QLabel()
        self._cls.setStyleSheet(
            "color:#A78BFA;font-size:13px;font-weight:800;background:transparent;")
        hint = QLabel("Esc · Ctrl+I")
        hint.setStyleSheet("color:#475569;font-size:9px;background:transparent;")
        hdr.addWidget(self._cls)
        hdr.addStretch()
        hdr.addWidget(hint)
        lay.addLayout(hdr)

        self._mod = QLabel()
        self._mod.setStyleSheet(
            "color:#475569;font-size:10px;background:transparent;margin-bottom:5px;")
        lay.addWidget(self._mod)

        sep = QLabel(); sep.setFixedHeight(1)
        sep.setStyleSheet("background:rgba(124,58,237,60);")
        lay.addWidget(sep)
        lay.addSpacing(6)

        self._body = QLabel()
        self._body.setWordWrap(True)
        self._body.setTextFormat(Qt.RichText)
        self._body.setStyleSheet(
            "color:#94A3B8;font-size:11px;background:transparent;")
        lay.addWidget(self._body)

    def show_for(self, widget: QWidget, gpos):
        print(f"[Inspector] show_for → {type(widget).__name__}  gpos={gpos}")

        self._cls.setText(type(widget).__name__)
        mod = type(widget).__module__
        self._mod.setText("" if mod == "__main__" else mod)
        self._body.setText(_build_info(widget))

        self.layout().activate()
        self.adjustSize()

        # Si adjustSize devuelve algo raro, forzar mínimo
        if self.height() < 80:
            self.resize(self._W, 220)

        print(f"[Inspector] tamaño panel: {self.width()}×{self.height()}")

        # Posicionar en coords globales
        screen = QApplication.primaryScreen().availableGeometry()
        x = gpos.x() + 18
        y = gpos.y() + 18
        if x + self.width()  > screen.right()  - 8:
            x = gpos.x() - self.width() - 12
        if y + self.height() > screen.bottom() - 8:
            y = gpos.y() - self.height() - 12

        self.move(x, y)
        self.show()
        self.raise_()
        print(f"[Inspector] visible={self.isVisible()}  pos={self.pos()}")

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.hide()
        super().keyPressEvent(e)


# ══════════════════════════════════════════════════════════════════════════════
#  BADGE
# ══════════════════════════════════════════════════════════════════════════════
class _Badge(QWidget):
    def __init__(self):
        super().__init__(None,
            Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setFixedSize(180, 28)
        self._t = 0.0
        QTimer(self, timeout=self._tick, interval=30).start()
        self.hide()

    def _tick(self):
        if self.isVisible():
            self._t = (self._t + 0.07) % (2 * math.pi)
            self.update()

    def place(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.right()-self.width()-16, screen.top()+16)
        self.show(); self.raise_()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect())
        pulse = (math.sin(self._t)+1)/2
        path = QPainterPath()
        path.addRoundedRect(rect, 7, 7)
        p.fillPath(path, QColor(8,10,22, int(215+30*pulse)))
        p.setPen(QPen(QColor(124,58,237, int(155+85*pulse)), 1.5))
        p.drawPath(path)
        p.setBrush(QColor(167,139,250, int(185+70*pulse)))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(14,14), 4, 4)
        p.setPen(QColor(200,180,255))
        p.setFont(QFont("Segoe UI", 9, QFont.Bold))
        p.drawText(QRectF(24,0,rect.width()-28,rect.height()),
                   Qt.AlignVCenter, "INSPECCIONANDO  Ctrl+I")


# ══════════════════════════════════════════════════════════════════════════════
#  Info builder
# ══════════════════════════════════════════════════════════════════════════════
def _row(label, value):
    return (f"<span style='color:#64748B'>{label}</span> "
            f"<span style='color:#CBD5E1'>{value}</span><br>")


def _build_info(w: QWidget) -> str:
    geo    = w.geometry()
    gpos   = w.mapToGlobal(w.rect().topLeft())
    parent = w.parent()
    wch    = [c for c in w.children() if isinstance(c, QWidget)]

    meta = w.metaObject()
    sigs = []
    for i in range(meta.methodCount()):
        m = meta.method(i)
        if m.methodType() == QMetaMethod.Signal:
            sigs.append(m.methodSignature().data().decode())

    parts = []
    name = w.objectName()
    parts.append(_row("nombre:",
        f'"{name}"' if name else '<i style="color:#475569">sin nombre</i>'))
    parts.append(_row("tamaño:",   f"{geo.width()} × {geo.height()} px"))
    parts.append(_row("posición:", f"({gpos.x()}, {gpos.y()})"))
    parts.append(_row("padre:",    type(parent).__name__ if parent else "—"))
    parts.append(_row("visible:",  "sí" if w.isVisible() else "no"))

    if wch:
        parts.append("<br>")
        parts.append(f"<span style='color:#22D3EE;font-weight:700'>hijos ({len(wch)})</span><br>")
        for c in wch[:6]:
            nm = (f' <span style="color:#475569">"{c.objectName()}"</span>'
                  if c.objectName() else "")
            parts.append(f"&nbsp;&nbsp;→ <span style='color:#94A3B8'>"
                         f"{type(c).__name__}</span>{nm}<br>")
        if len(wch) > 6:
            parts.append(f"&nbsp;&nbsp;<span style='color:#475569'>"
                         f"+{len(wch)-6} más</span><br>")

    if sigs:
        parts.append("<br>")
        parts.append(f"<span style='color:#F472B6;font-weight:700'>"
                     f"señales ({len(sigs)})</span><br>")
        for s in sigs[:8]:
            parts.append(f"&nbsp;&nbsp;<span style='color:#94A3B8'>• {s}</span><br>")
        if len(sigs) > 8:
            parts.append(f"&nbsp;&nbsp;<span style='color:#475569'>"
                         f"+{len(sigs)-8} más</span><br>")

    ss = w.styleSheet().strip()
    if ss:
        preview = ss.replace("<","&lt;").replace(">","&gt;")
        if len(preview) > 160: preview = preview[:160]+"…"
        parts.append("<br>")
        parts.append(f"<span style='color:#34D399;font-weight:700'>stylesheet</span><br>"
                     f"<span style='color:#475569;font-size:10px'>{preview}</span>")

    return "".join(parts)


# ══════════════════════════════════════════════════════════════════════════════
#  INSPECTOR
# ══════════════════════════════════════════════════════════════════════════════
class Inspector(QObject):
    def __init__(self, app: QApplication, main_window: QWidget):
        super().__init__(app)
        self._active  = False
        self._mw      = main_window
        self._overlay = _Overlay()
        self._panel   = _Panel(main_window)
        self._badge   = _Badge()

        # QShortcut con ApplicationShortcut: funciona independientemente del foco
        sc = QShortcut(QKeySequence("Ctrl+I"), main_window)
        sc.setContext(Qt.ApplicationShortcut)
        sc.activated.connect(self.toggle)
        print("[Inspector] QShortcut Ctrl+I registrado")

        app.installEventFilter(self)

    def toggle(self):
        self._active = not self._active
        print(f"[Inspector] toggle → activo={self._active}")
        if self._active:
            QApplication.setOverrideCursor(Qt.CrossCursor)
            self._badge.place()
        else:
            QApplication.restoreOverrideCursor()
            self._overlay.hide()
            self._panel.hide()
            self._badge.hide()

    def _is_own(self, w: QWidget) -> bool:
        own = (self._overlay, self._panel, self._badge)
        node = w
        while node is not None:
            if node in own:
                return True
            p = node.parent()
            node = p if isinstance(p, QWidget) else None
        return False

    def eventFilter(self, obj, event):
        if not self._active:
            return False
        if not isinstance(obj, QWidget) or self._is_own(obj):
            return False

        t = event.type()

        if t == QEvent.MouseMove:
            self._overlay.track(obj)

        elif t == QEvent.MouseButtonPress:
            self._panel.show_for(obj, QCursor.pos())
            return True

        elif t == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            if self._panel.isVisible():
                self._panel.hide()
            else:
                self.toggle()
            return True

        return False
