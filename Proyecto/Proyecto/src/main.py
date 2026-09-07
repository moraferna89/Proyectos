import sys
from PyQt5.QtWidgets import QApplication, QDialog
from src.gui.main_window import MainWindow
from src.backend import *

app = QApplication([])

while True:
    # Mostrar ventana de login
    login = LoginWindow()
    if login.exec_() == QDialog.Accepted:
        # Usuario válido → abrir ventana principal
        window = MainWindow(login.tipo_usuario, login.id_usuario)
        window.show()

        # Ejecutar la app hasta que se cierre la ventana principal
        app.exec_()

        # 🔁 Si el usuario cerró sesión, volvemos a mostrar login
        # (cerrarSesion en el Bridge solo cierra la ventana principal)
        continue
    else:
        # Si el usuario cierra el login, terminamos el programa
        break

sys.exit()
