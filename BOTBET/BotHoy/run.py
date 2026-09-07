import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))


def _start_scheduler():
    from apscheduler.schedulers.background import BackgroundScheduler
    from backend.telegram_notifier import run_signal_sync
    from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Scheduler] TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no configurados — scheduler desactivado.")
        return

    scheduler = BackgroundScheduler()
    # Ejecutar inmediatamente al arrancar y luego cada 6 horas
    scheduler.add_job(run_signal_sync, "date", id="signal_boot")
    scheduler.add_job(run_signal_sync, "interval", hours=6, id="signal_interval")
    scheduler.start()
    print("[Scheduler] Activo — señales Telegram cada 6 horas.")


def _start_server():
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="warning",
    )


def _wait_for_server(url: str, timeout: float = 10.0):
    import urllib.request
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=1)
            return
        except Exception:
            time.sleep(0.2)


class AppAPI:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def launch(self):
        """Expande la ventana desde el centro con animación ease-out."""
        if not self._window:
            return
        import threading, time, ctypes
        user32 = ctypes.windll.user32
        screen_w = user32.GetSystemMetrics(0)
        screen_h = user32.GetSystemMetrics(1)
        cx = screen_w // 2
        cy = screen_h // 2
        w0, h0 = 400, 360
        w1, h1 = 1280, 820
        steps = 45
        dt = 0.50 / steps          # duración total 500 ms

        def _animate():
            for i in range(1, steps + 1):
                t = i / steps
                ease = 1 - (1 - t) ** 3   # ease-out cúbico
                w = int(w0 + (w1 - w0) * ease)
                h = int(h0 + (h1 - h0) * ease)
                self._window.move(cx - w // 2, cy - h // 2)
                self._window.resize(w, h)
                time.sleep(dt)

        threading.Thread(target=_animate, daemon=True).start()

    def close_window(self):
        if self._window:
            self._window.destroy()

    def minimize_window(self):
        if self._window:
            self._window.minimize()

    def get_pos(self):
        if self._window:
            return {"x": self._window.x, "y": self._window.y}
        return {"x": 0, "y": 0}

    def move_window(self, x, y):
        if self._window:
            self._window.move(int(x), int(y))

    # ── Telegram scheduler ──────────────────────────────────────────
    def _pid_file(self):
        return ROOT / "logs" / "scheduler.pid"

    @staticmethod
    def _pid_alive(pid: int) -> bool:
        """Comprueba si un PID existe en Windows."""
        import ctypes
        PROCESS_QUERY_INFORMATION = 0x0400
        STILL_ACTIVE = 259
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
            return code.value == STILL_ACTIVE
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)

    @staticmethod
    def _pid_kill(pid: int):
        """Termina un proceso en Windows."""
        import ctypes
        PROCESS_TERMINATE = 0x0001
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
        if handle:
            ctypes.windll.kernel32.TerminateProcess(handle, 1)
            ctypes.windll.kernel32.CloseHandle(handle)

    def scheduler_status(self) -> bool:
        pid_file = self._pid_file()
        if not pid_file.exists():
            return False
        try:
            pid = int(pid_file.read_text().strip())
            if self._pid_alive(pid):
                return True
            pid_file.unlink(missing_ok=True)
            return False
        except (ValueError, Exception):
            pid_file.unlink(missing_ok=True)
            return False

    def scheduler_start(self):
        if self.scheduler_status():
            return {"ok": True, "running": True}
        import subprocess, time as _t
        subprocess.Popen(
            [sys.executable, str(ROOT / "bot_scheduler.py")],
            cwd=str(ROOT),
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        for _ in range(15):          # esperar hasta 3 s al PID file
            _t.sleep(0.2)
            if self._pid_file().exists():
                break
        return {"ok": True, "running": self.scheduler_status()}

    def scheduler_stop(self):
        pid_file = self._pid_file()
        if not pid_file.exists():
            return {"ok": True, "running": False}
        try:
            pid = int(pid_file.read_text().strip())
            self._pid_kill(pid)
        except Exception:
            pass
        pid_file.unlink(missing_ok=True)
        return {"ok": True, "running": False}


def main():
    import webview

    server_thread = threading.Thread(target=_start_server, daemon=True)
    server_thread.start()
    _wait_for_server("http://127.0.0.1:8000/api/health")

    _start_scheduler()

    api = AppAPI()

    import ctypes
    _u32 = ctypes.windll.user32
    _sw  = _u32.GetSystemMetrics(0)
    _sh  = _u32.GetSystemMetrics(1)
    _x   = (_sw - 400) // 2
    _y   = (_sh - 360) // 2

    window = webview.create_window(
        title="BOTBET",
        url="http://127.0.0.1:8000",
        width=400,
        height=360,
        x=_x,
        y=_y,
        min_size=(400, 360),
        resizable=True,
        frameless=True,
        js_api=api,
    )
    api.set_window(window)
    webview.start(debug=False)


if __name__ == "__main__":
    main()
