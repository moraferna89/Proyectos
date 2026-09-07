import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QSpacerItem, QSizePolicy,
    QApplication
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QUrl , Qt , QTimer
from PyQt5.QtGui import QPixmap
import json
import base64
from src.backend import *
from src.db import *
from datetime import datetime, date
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAGE_DIR = os.path.join(os.path.dirname(__file__), "pages")


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setFixedHeight(35)
        self.setStyleSheet("background-color: #0b0b0b;")  # Fondo negro sólido

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(5, 0, 0, 0)
        main_layout.setSpacing(0)

        # ----------------- LOGO + TITULO -----------------
        logo_title_layout = QHBoxLayout()
        logo_title_layout.setContentsMargins(0, 0, 0, 0)
        logo_title_layout.setSpacing(10)

        # Determinar base_dir
        if getattr(sys, 'frozen', False):
            BASE_DIR = sys._MEIPASS
        else:
            # Desde src/gui/… subimos dos niveles: src/gui -> src -> proyecto
            BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

        logo_path = os.path.join(BASE_DIR, "assets", "logos", "logochico.png")
        print("Ruta logo:", logo_path)

        pixmap = QPixmap(logo_path)
        if pixmap.isNull():
            print("Error: no se pudo cargar la imagen del logo")

        # Logo
        self.logo = QLabel()
        pixmap = QPixmap(logo_path)
        if pixmap.isNull():
            print("Error: no se pudo cargar la imagen del logo:", logo_path)
        else:
            pixmap = pixmap.scaledToHeight(25, Qt.SmoothTransformation)
            self.logo.setPixmap(pixmap)
        self.logo.setAlignment(Qt.AlignVCenter)

        # Título
        self.title = QLabel("Call Flash - Escritorio")
        self.title.setStyleSheet("""
            color: white;
            font-weight: bold;
            font-size: 14px;
            background: transparent;
            padding: 0;
            margin: 0;
        """)
        self.title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        logo_title_layout.addWidget(self.logo)
        logo_title_layout.addWidget(self.title)

        # Spacer entre logo+titulo y botones
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # ----------------- BOTONES -----------------
        button_style = """
            QPushButton {
                background-color: #0b0b0b;
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333;
            }
            QPushButton:pressed {
                background-color: #555;
            }
        """

        self.minimize_btn = QPushButton("–")
        self.maximize_btn = QPushButton("□")
        self.close_btn = QPushButton("×")

        for btn in [self.minimize_btn, self.maximize_btn, self.close_btn]:
            btn.setFixedWidth(35)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(button_style)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)  # Ocupa toda la altura

        # Conexiones
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self.parent.close)

        # Layout final
        main_layout.addLayout(logo_title_layout)
        main_layout.addItem(spacer)
        main_layout.addWidget(self.minimize_btn)
        main_layout.addWidget(self.maximize_btn)
        main_layout.addWidget(self.close_btn)

        self.setLayout(main_layout)

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    # Permitir mover la ventana arrastrando la barra
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if hasattr(self, "offset") and event.buttons() == Qt.LeftButton:
            self.parent.move(event.globalPos() - self.offset)








# -------------------------------------------------
# 🔹 Ventana principal
# -------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self,usuario,id_usuario):
        super().__init__()
        
        self.setWindowTitle("App de Escritorio PyQt5 + HTML + MySQL")
                # Obtener tamaño de la pantalla
        screen = QApplication.primaryScreen()
        size = screen.size()
        screen_width = size.width()
        screen_height = size.height()

        # Ajustar ventana al 80% del ancho y alto de la pantalla
        width = int(screen_width * 0.8)
        height = int(screen_height * 0.8)

        self.resize(width, height)

        self.datos_llamada_actual = None

        # QMainWindow sin bordes del sistema
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #0b0b0b; color: white;")

        # Contenedor principal
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: #0b0b0b;")

        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Agregar barra superior
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        # Contenedor horizontal (menú + contenido)
        contenedor = QWidget()
        contenedor.setStyleSheet("background-color: #000;")
        layout = QHBoxLayout(contenedor)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # WebViews: menú y contenido
        self.menu_view = QWebEngineView()
        self.content_view = QWebEngineView()
        self.menu_view.setStyleSheet("background: #000; border: none;")
        self.content_view.setStyleSheet("background: #000; border: none;")

        layout.addWidget(self.menu_view, 1)
        layout.addWidget(self.content_view, 5)

        main_layout.addWidget(contenedor)
        self.setCentralWidget(main_widget)

        # Canal de comunicación
        self.channel = QWebChannel()
        self.bridge = Bridge(self)
        self.channel.registerObject("bridge", self.bridge)
        self.menu_view.page().setWebChannel(self.channel)
        self.content_view.page().setWebChannel(self.channel)

        # Al inicializar MainWindow
        self.id_usuario = id_usuario
        print(id_usuario)
        self.usuario = usuario  # llega como "admin" o "otro"
        print(usuario)

        # Cargar menú y página inicial según usuario
        self.load_menu()
        if self.usuario == "admin":
            self.load_page("inicio.html")
        else:
            self.load_page("inicio_ejecutivo.html")

        # ---------------------
    def load_menu(self):
        if self.usuario == "admin":
            archivo = "menu.html"
            carpeta = "admin"
        else:
            archivo = "menu_otro.html"
            carpeta = "otro"

        path = os.path.join(BASE_DIR, "pages", carpeta, archivo)
        self.menu_view.load(QUrl.fromLocalFile(path))


    def load_page(self, archivo):
        carpeta = "admin" if self.usuario == "admin" else "otro"
        path = os.path.join(PAGE_DIR, carpeta, archivo)

        if not os.path.exists(path):
            print(f"⚠️ Archivo no encontrado: {path}")
            return

        url = QUrl.fromLocalFile(path)

        if self.usuario == "admin":
            if "ejecutivos.html" in archivo:
                self.cargar_tabla_ejecutivos(url)
            elif "llamadas.html" in archivo:
                self.cargar_tabla_llamadas(url)
            elif "inicio.html" in archivo:
                self.cargar_scroll_nombres(url)
            else:
                self.content_view.load(url)
        else:
            if "inicio_ejecutivo.html" in archivo:
                self.cargar_tabla_llamadasxid(url)
            if "mis_llamadas.html" in archivo:
                self.cargar_tabla_todasllamadasxid(url)
            else:
                self.content_view.load(url)



    def actualizar_ranking(self):
        """
        Consulta top 3 ejecutivos y actualiza el HTML en el QWebEngineView.
        """
        top3 = obtener_top3_efectividad()  # [{"ejecutivo": "Juan", ...}, ...]

        ids_avatar = ["avatar1", "avatar2", "avatar3"]

        for i, data in enumerate(top3):
            nombre = data["ejecutivo"]
            js = f'document.getElementById("{ids_avatar[i]}").textContent = "{nombre}";'
            self.content_view.page().runJavaScript(js)

    def inyectar_tabla_ejecutivos(self, datos):
        if datos:
            columnas_visibles = [
                "id_ejecutivo", 
                "Rut_Ejecutivo", 
                "Nombre_Ejecutivo", 
                "Apellido_Ejecutivo",
                "TCARGO_Id_Tipo_Cargo"
            ]
            nombres_columnas = {
                "id_ejecutivo": "ID",
                "Rut_Ejecutivo": "Rut",
                "Nombre_Ejecutivo": "Nombre",
                "Apellido_Ejecutivo": "Apellido",
                "TCARGO_Id_Tipo_Cargo": "Cargo"
            }

            th_html = "".join(f"<th>{nombres_columnas.get(col, col)}</th>" for col in columnas_visibles)
            filas_html = "".join(
                "<tr>" + "".join(f"<td>{fila[col]}</td>" for col in columnas_visibles) + "</tr>"
                for fila in datos
            )

            js = f"""
            (function() {{
                const tabla = document.querySelector("#tabla-ejecutivos table");
                if (!tabla) return;  // Evita errores si la tabla no existe aún
                tabla.querySelector("thead").innerHTML = "<tr>{th_html}</tr>";
                tabla.querySelector("tbody").innerHTML = `{filas_html}`;
            }})();
            """
            self.content_view.page().runJavaScript(js)
        else:
            self.content_view.page().runJavaScript(
                'document.getElementById("tabla-ejecutivos").innerHTML = "<p>No hay ejecutivos disponibles.</p>";'
            )

    def cargar_tabla_ejecutivos(self, url):
        """
        Carga la tabla de ejecutivos en content_view.
        """
        try:
            datos = obtener_ejecutivos()
        except Exception as e:
            error_html = f"<p>Error de conexión a BD: {e}</p>"
            self.content_view.load(url)
            self.content_view.loadFinished.connect(
                lambda ok: self.content_view.page().runJavaScript(
                    f'document.getElementById("tabla-ejecutivos").innerHTML = `{error_html}`;'
                )
            )
            return

        def on_load_finished(ok):
            self.inyectar_tabla_ejecutivos(datos)
            self.content_view.loadFinished.disconnect(on_load_finished)

        self.content_view.load(url)
        self.content_view.loadFinished.connect(on_load_finished)



    def cargar_scroll_nombres(self, url):
        try:
            datos = obtener_ejecutivos()
        except Exception as e:
            error_html = f"<p>Error de conexión a BD: {e}</p>"
            self.content_view.load(url)
            self.content_view.loadFinished.connect(
                lambda ok: self.content_view.page().runJavaScript(
                    f'document.querySelector(".scroll-container").innerHTML = `{error_html}`;'
                )
            )
            return

        def inyectar_nombres(ok):
            if datos:
                nombres_html = "".join(f"<div class='item'>{c['Nombre_Ejecutivo']}</div>" for c in datos)
                self.content_view.page().runJavaScript(
                    f'document.querySelector(".scroll-container").innerHTML = `{nombres_html}`;'
                )
            else:
                self.content_view.page().runJavaScript(
                    'document.querySelector(".scroll-container").innerHTML = "<p>No hay clientes.</p>";'
                )
            self.content_view.loadFinished.disconnect(inyectar_nombres)

        self.content_view.load(url)
        self.content_view.loadFinished.connect(inyectar_nombres)
    


    def inyectar_tabla_llamadas(self, datos):
        """
        Inyecta los datos de llamadas en la tabla HTML, agregando un botón 'Ver Detalles' en cada fila.
        La columna de clasificación se muestra con estrellas según el valor (1-7).
        Muestra fecha y hora correctamente.
        """

        if not datos:
            js = 'document.querySelector("#tabla-llamadas table tbody").innerHTML = "<tr><td colspan=100%>No hay llamadas disponibles.</td></tr>";'
            self.content_view.page().runJavaScript(js)
            return

        columnas_visibles = [
            "id_llamadas",
            "Fecha",
            "Hora",
            "EJECUTIVO_Id_ejecutivo",
            "CLIENTE_Id_cliente",
            "SUPERVISOR_Id_supervisor",
            "CLASIFI_LLAMADA_Id_Clasifi_Llam"
        ]

        nombres_columnas = {
            "id_llamadas": "ID",
            "Fecha": "Fecha",
            "Hora": "Hora",
            "EJECUTIVO_Id_ejecutivo": "Ejecutivo",
            "CLIENTE_Id_cliente": "Cliente",
            "SUPERVISOR_Id_supervisor": "Supervisor",
            "CLASIFI_LLAMADA_Id_Clasifi_Llam": "Clasificación"
        }

        columnas = [c for c in columnas_visibles if c.lower() != "audio_llamada"]

        th_html = "".join(f"<th>{nombres_columnas.get(col, col)}</th>" for col in columnas)
        th_html += "<th>Acción</th>"

        filas_html = ""
        for fila in datos:
            fila_html = ""
            fecha_str = str(fila.get("Fecha", ""))  # YYYY-MM-DD 00:00:00
            hora_completa = str(fila.get("Hora", ""))  # YYYY-MM-DD HH:MM:SS
            hora_str = hora_completa.split(" ")[1] if " " in hora_completa else hora_completa

            for col in columnas:
                valor = fila.get(col, "")
                if col == "Fecha":
                    valor = fecha_str.split(" ")[0]  # solo YYYY-MM-DD
                elif col == "Hora":
                    valor = hora_str  # solo HH:MM:SS
                elif col == "CLASIFI_LLAMADA_Id_Clasifi_Llam":
                    try:
                        n = int(valor)
                        estrellas_html = ""
                        for i in range(1, 8):
                            if i <= n:
                                estrellas_html += '<span class="estrella llena">★</span>'
                            else:
                                estrellas_html += '<span class="estrella vacia">★</span>'
                        valor = estrellas_html
                    except:
                        valor = '<span class="estrella vacia">★</span>' * 7

                fila_html += f"<td>{valor}</td>"

            id_llamada = fila.get("Id_Llamadas") or fila.get("id_llamadas") or fila.get("id_llamada")
            fila_html += f"<td><button class='ver-detalles' onclick='verDetalles({id_llamada})'>Ver Detalles</button></td>"
            filas_html += f"<tr>{fila_html}</tr>"

        js = f"""
        (function() {{
            const tabla = document.querySelector("#tabla-llamadas table");
            tabla.querySelector("thead").innerHTML = "<tr>{th_html}</tr>";
            tabla.querySelector("tbody").innerHTML = `{filas_html}`;
        }})();
        """

        self.content_view.page().runJavaScript(js)





    def cargar_tabla_llamadas(self, url):
        # Carga llamadas desde DB e inyecta en HTML
        try:
            datos = obtener_llamadas()
        except Exception as e:
            error_html = f"<p>Error de conexión a BD: {e}</p>"
            self.content_view.load(url)
            self.content_view.loadFinished.connect(
                lambda ok: self.content_view.page().runJavaScript(
                    f'document.getElementById("tabla-llamadas").innerHTML = `{error_html}`;'
                )
            )
            return

        def on_load(ok):
            self.inyectar_tabla_llamadas(datos)
            self.content_view.loadFinished.disconnect(on_load)

        self.content_view.load(url)
        self.content_view.loadFinished.connect(on_load)


    def cargar_detalle_llamada(self, id_llamada):
        """
        Carga la página de detalle de la llamada específica en content_view,
        inyectando los datos de la llamada y su audio.
        """
        try:
            # 🔹 Obtener la llamada por ID
            datos = obtener_llamada_por_id(id_llamada)
            if not datos:
                print(f"No se encontró la llamada con ID {id_llamada}")
                return

            # 🔹 Convertir fechas a string
            for key, value in datos.items():
                if isinstance(value, (datetime, date)):
                    datos[key] = value.strftime("%Y-%m-%d %H:%M:%S")

            # 🔹 Convertir audio a base64 si existe
            if datos.get("audio_llamada"):
                datos["audio_llamada"] = base64.b64encode(datos["audio_llamada"]).decode("utf-8")
            else:
                datos["audio_llamada"] = None

            print("\n===== DEBUG: DATOS QUE SE ENVIAN A JS (SIN AUDIO) =====")
            for k, v in datos.items():
                if k != "audio_llamada":  # evita imprimir el base64
                    print(f"{k}: {v}")
            print("=======================================================\n")

            # 🔹 Guardar en el bridge (para transcripción o accesos desde JS)
            if hasattr(self, 'bridge') and self.bridge:
                self.bridge.datos_llamada_actual = None  # Limpiar anterior
                self.bridge.datos_llamada_actual = datos
                print("DEBUG: bridge.datos_llamada_actual actualizado para ID", id_llamada)

            datos_json = json.dumps(datos, ensure_ascii=False)

            # 🔹 Ruta del HTML
            url = QUrl.fromLocalFile(os.path.join(BASE_DIR, "pages","admin", "detalle_llamada.html"))

            # 🔹 Handler único para cargar los datos cuando la página termine de cargar
            def on_load(ok):
                if ok:
                    js = f"if (typeof cargarDetalle === 'function') cargarDetalle({datos_json});"
                    self.content_view.page().runJavaScript(js)
                else:
                    print("❌ Error al cargar detalle_llamada.html")

                # ⚡ Desconectar **solo este handler** inmediatamente después
                try:
                    self.content_view.page().loadFinished.disconnect(on_load)
                except Exception:
                    pass

            # 🔹 Conectar solo este handler
            self.content_view.page().loadFinished.connect(on_load)

            # 🔹 Cargar la página
            self.content_view.setUrl(url)

        except Exception as e:
            print("Error al cargar detalle de llamada:", e)
        
    def cargar_detalle_llamada_xejecutivo(self, id_llamada):
        """
        Carga la página de detalle de la llamada específica en content_view,
        inyectando los datos de la llamada y su audio.
        """
        try:
            # 🔹 Obtener la llamada por ID
            datos = obtener_llamada_por_id(id_llamada)
            if not datos:
                print(f"No se encontró la llamada con ID {id_llamada}")
                return

            # 🔹 Convertir fechas a string
            for key, value in datos.items():
                if isinstance(value, (datetime, date)):
                    datos[key] = value.strftime("%Y-%m-%d %H:%M:%S")

            # 🔹 Convertir audio a base64 si existe
            if datos.get("audio_llamada"):
                datos["audio_llamada"] = base64.b64encode(datos["audio_llamada"]).decode("utf-8")
            else:
                datos["audio_llamada"] = None

            print("\n===== DEBUG: DATOS QUE SE ENVIAN A JS (SIN AUDIO) =====")
            for k, v in datos.items():
                if k != "audio_llamada":  # evita imprimir el base64
                    print(f"{k}: {v}")
            print("=======================================================\n")

            # 🔹 Guardar en el bridge (para transcripción o accesos desde JS)
            if hasattr(self, 'bridge') and self.bridge:
                self.bridge.datos_llamada_actual = None  # Limpiar anterior
                self.bridge.datos_llamada_actual = datos
                print("DEBUG: bridge.datos_llamada_actual actualizado para ID", id_llamada)

            datos_json = json.dumps(datos, ensure_ascii=False)

            # 🔹 Ruta del HTML
            url = QUrl.fromLocalFile(os.path.join(BASE_DIR, "pages","otro", "detalle_llamada.html"))

            # 🔹 Handler único para cargar los datos cuando la página termine de cargar
            def on_load(ok):
                if ok:
                    js = f"if (typeof cargarDetalle === 'function') cargarDetalle({datos_json});"
                    self.content_view.page().runJavaScript(js)
                else:
                    print("❌ Error al cargar detalle_llamada.html")

                # ⚡ Desconectar **solo este handler** inmediatamente después
                try:
                    self.content_view.page().loadFinished.disconnect(on_load)
                except Exception:
                    pass

            # 🔹 Conectar solo este handler
            self.content_view.page().loadFinished.connect(on_load)

            # 🔹 Cargar la página
            self.content_view.setUrl(url)

        except Exception as e:
            print("Error al cargar detalle de llamada:", e)




    def enviar_datos_detalle(self, datos_json):
        js = f"if (typeof cargarDetalle === 'function') cargarDetalle({datos_json});"
        self.content_view.page().runJavaScript(js)


    def load_detalle_llamada(self, id_llamada):
        """
        Carga la página de detalle de la llamada específica en content_view,
        manteniendo el menú a la izquierda.
        """
        # Obtener los datos de la llamada
        llamada = obtener_llamada_por_id(id_llamada)
        if not llamada:
            print(f"No se encontró la llamada con ID {id_llamada}")
            return

        # Ruta del HTML de detalles
        path = os.path.join(BASE_DIR, "pages", "detalle_llamada.html")
        url = QUrl.fromLocalFile(path)
        
        def on_load(ok):
            # Inyectar los datos de la llamada en el HTML
            detalles_html = "".join(f"<p><strong>{k}:</strong> {v}</p>" for k, v in llamada.items())
            js = f"""
                document.getElementById('detalle-llamada').innerHTML = `{detalles_html}`;
                document.getElementById('btn-volver').onclick = function() {{
                    bridge.volverTablaLlamadas();
                }};
            """
            self.content_view.page().runJavaScript(js)
            self.content_view.loadFinished.disconnect(on_load)

        self.content_view.load(url)
        self.content_view.loadFinished.connect(on_load)

    # main_window.py
    def abrir_agregar_supervisor(self):
        dialog = AgregarSupervisorDialog(self)
        dialog.exec_()  # Esto bloquea hasta cerrar el diálogo

    def abrir_editar_supervisor(self):
        dialog = EditarSupervisorDialog(self)
        dialog.exec_()
    
    def abrir_eliminar_supervisor(self):
        dialog = EliminarSupervisorDialog(self)
        dialog.exec_()


    def abrir_agregar_ejecutivo(self):
        dialog = AgregarEjecutivoDialog(self)
        dialog.exec_()  # Esto bloquea hasta cerrar el diálogo

    def abrir_editar_ejecutivo(self):
        dialog = EditarEjecutivoDialog(self)
        dialog.exec_()
    
    def abrir_eliminar_ejecutivo(self):
        dialog = EliminarEjecutivoDialog(self)
        dialog.exec_()

    def abrir_agregar_cliente(self):
        dialog = AgregarClienteDialog(self)
        dialog.exec_()
    
    def abrir_eliminar_cliente(self):
        dialog = EliminarClienteDialog(self)
        dialog.exec_()

    def abrir_agregar_llamada(self):
        dialog = AgregarLlamadaDialog(self)
        dialog.exec_()

    def abrir_eliminar_llamada(self):
        dialog = EliminarLlamadaDialog(self)
        dialog.exec_()

    def abrir_editar_cliente(self):
        dialog = EditarClienteDialog(self)
        dialog.exec_()

    def inyectar_tabla_llamadasxid(self, datos):
        """
        Inyecta en el HTML los datos de llamadas correspondientes al ejecutivo logueado.
        Incluye depuración visual y de consola.
        """
        print("🟦 [inyectar_tabla_llamadasxid] Iniciando inyección...")
        print(f"🟨 Cantidad de registros: {len(datos)}")

        # Caso sin datos
        if not datos:
            print("⚠️ No se recibieron datos, mostrando mensaje vacío.")
            js = (
                "console.log('⚠️ No hay llamadas disponibles');"
                "document.querySelector('#tabla-llamadasxid table tbody').innerHTML = "
                "\"<tr><td colspan=100%>No hay llamadas disponibles.</td></tr>\";"
            )
            self.content_view.page().runJavaScript(js)
            return

        # Columnas visibles
        columnas_visibles = [
            "Fecha",
            "Hora",
            "CLASIFI_LLAMADA_Id_Clasifi_Llam",
        ]

        nombres_columnas = {
            "id_llamadas": "ID Llamada",
            "Fecha": "Fecha",
            "Hora": "Hora",
            "CLIENTE_Id_cliente": "Cliente",
            "SUPERVISOR_Id_supervisor": "Supervisor",
            "CLASIFI_LLAMADA_Id_Clasifi_Llam": "Clasificación",
            "Rut_Ejecutivo": "RUT",
            "Nombre_Ejecutivo": "Nombre",
            "Apellido_Ejecutivo": "Apellido",
            "TCARGO_Id_Tipo_Cargo": "Cargo",
        }

        # Encabezados
        th_html = "".join(f"<th>{nombres_columnas.get(col, col)}</th>" for col in columnas_visibles)

        filas_html = ""
        for i, fila in enumerate(datos, start=1):
            fila_html = ""
            fecha_str = str(fila.get("Fecha", ""))[:10]
            hora_str = str(fila.get("Hora", ""))[-8:]

            for col in columnas_visibles:
                valor = fila.get(col, "")
                if col == "Fecha":
                    valor = fecha_str
                elif col == "Hora":
                    valor = hora_str
                elif col == "CLASIFI_LLAMADA_Id_Clasifi_Llam":
                    try:
                        n = int(valor)
                        valor = "".join(
                            '<span class=\"estrella llena\">★</span>' if i <= n else '<span class=\"estrella vacia\">★</span>'
                            for i in range(1, 8)
                        )
                    except:
                        valor = '<span class=\"estrella vacia\">★</span>' * 7
                fila_html += f"<td>{valor}</td>"

            id_llamada = fila.get("id_llamadas") or fila.get("Id_Llamadas")
            filas_html += f"<tr>{fila_html}</tr>"

        # Inyección con consola y alerta JS
        js = f"""
        (function() {{
            console.log("✅ Ejecutando script de inyección de tabla...");
            const contenedor = document.querySelector("#tabla-llamadasxid");
            if (!contenedor) {{
                alert("❌ No se encontró el contenedor #tabla-llamadasxid");
                console.error("❌ No se encontró el contenedor #tabla-llamadasxid");
                return;
            }}

            const tabla = contenedor.querySelector("table");
            if (!tabla) {{
                alert("❌ No se encontró la tabla dentro del contenedor");
                console.error("❌ No se encontró la tabla dentro del contenedor");
                return;
            }}

            tabla.querySelector("thead").innerHTML = "<tr>{th_html}</tr>";
            tabla.querySelector("tbody").innerHTML = `{filas_html}`;
            console.log("✅ Tabla inyectada correctamente con {len(datos)} filas.");
        }})();
        """

        print("🟩 Inyectando JS en página...")
        self.content_view.page().runJavaScript(js)
        print("🟩 JS enviado al motor WebEngine.")


    def cargar_tabla_llamadasxid(self, url):
        print("🟦 [cargar_tabla_llamadasxid] Cargando tabla para el ejecutivo...")
        id_ejecutivo = getattr(self, "id_usuario", None)
        if not id_ejecutivo:
            print("❌ No se encontró el ID del ejecutivo.")
            return

        datos = obtener_llamadas_xejecutivo(id_ejecutivo)
        print(f"🟩 Se obtuvieron {len(datos)} filas desde la BD.")

        def inyectar_despues():
            print("🕓 Esperando a que cargue la página...")
            self.inyectar_tabla_llamadasxid(datos)

        # Espera 500ms después de la carga del HTML
        def on_load(ok):
            QTimer.singleShot(100, inyectar_despues)
            self.content_view.loadFinished.disconnect(on_load)

        self.content_view.load(url)
        self.content_view.loadFinished.connect(on_load)


    



    def inyectar_tabla_todasllamadasxid(self, datos):
        """
        Inyecta en el HTML los datos de llamadas correspondientes al ejecutivo logueado.
        Incluye depuración visual y de consola.
        """
        print("🟦 [inyectar_tabla_todasllamadasxid] Iniciando inyección...")
        print(f"🟨 Cantidad de registros: {len(datos)}")

        # Caso sin datos
        if not datos:
            print("⚠️ No se recibieron datos, mostrando mensaje vacío.")
            js = (
                "console.log('⚠️ No hay llamadas disponibles');"
                "document.querySelector('#tabla-todasllamadasxid table tbody').innerHTML = "
                "\"<tr><td colspan=100%>No hay llamadas disponibles.</td></tr>\";"
            )
            self.content_view.page().runJavaScript(js)
            return

        # Columnas visibles
        columnas_visibles = [
            "id_llamadas",
            "Fecha",
            "Hora",
            "CLASIFI_LLAMADA_Id_Clasifi_Llam",
        ]

        nombres_columnas = {
            "id_llamadas": "ID Llamada",
            "Fecha": "Fecha",
            "Hora": "Hora",
            "CLIENTE_Id_cliente": "Cliente",
            "SUPERVISOR_Id_supervisor": "Supervisor",
            "CLASIFI_LLAMADA_Id_Clasifi_Llam": "Clasificación",
            "Rut_Ejecutivo": "RUT",
            "Nombre_Ejecutivo": "Nombre",
            "Apellido_Ejecutivo": "Apellido",
            "TCARGO_Id_Tipo_Cargo": "Cargo",
        }

        # Encabezados
        th_html = "".join(f"<th>{nombres_columnas.get(col, col)}</th>" for col in columnas_visibles)
        th_html += "<th>Acción</th>"

        filas_html = ""
        for i, fila in enumerate(datos, start=1):
            fila_html = ""
            fecha_str = str(fila.get("Fecha", ""))[:10]
            hora_str = str(fila.get("Hora", ""))[-8:]

            for col in columnas_visibles:
                valor = fila.get(col, "")
                if col == "Fecha":
                    valor = fecha_str
                elif col == "Hora":
                    valor = hora_str
                elif col == "CLASIFI_LLAMADA_Id_Clasifi_Llam":
                    try:
                        n = int(valor)
                        valor = "".join(
                            '<span class=\"estrella llena\">★</span>' if i <= n else '<span class=\"estrella vacia\">★</span>'
                            for i in range(1, 8)
                        )
                    except:
                        valor = '<span class=\"estrella vacia\">★</span>' * 7
                fila_html += f"<td>{valor}</td>"

            id_llamada = fila.get("id_llamadas") or fila.get("Id_Llamadas")
            fila_html += f"<td><button class='ver-detalles' onclick='verDetalles({id_llamada})'>Ver Detalles</button></td>"
            filas_html += f"<tr>{fila_html}</tr>"

        # Inyección con consola y alerta JS
        js = f"""
        (function() {{
            console.log("✅ Ejecutando script de inyección de tabla...");
            const contenedor = document.querySelector("#tabla-todasllamadasxid");
            if (!contenedor) {{
                alert("❌ No se encontró el contenedor #tabla-todasllamadasxid");
                console.error("❌ No se encontró el contenedor #tabla-todasllamadasxid");
                return;
            }}

            const tabla = contenedor.querySelector("table");
            if (!tabla) {{
                alert("❌ No se encontró la tabla dentro del contenedor");
                console.error("❌ No se encontró la tabla dentro del contenedor");
                return;
            }}

            tabla.querySelector("thead").innerHTML = "<tr>{th_html}</tr>";
            tabla.querySelector("tbody").innerHTML = `{filas_html}`;
            console.log("✅ Tabla inyectada correctamente con {len(datos)} filas.");
        }})();
        """

        print("🟩 Inyectando JS en página...")
        self.content_view.page().runJavaScript(js)
        print("🟩 JS enviado al motor WebEngine.")


    def cargar_tabla_todasllamadasxid(self, url):
        print("🟦 [cargar_tabla_todasllamadasxid] Cargando tabla para el ejecutivo...")
        id_ejecutivo = getattr(self, "id_usuario", None)
        if not id_ejecutivo:
            print("❌ No se encontró el ID del ejecutivo.")
            return

        datos = obtener_todasllamadas_xejecutivo(id_ejecutivo)
        print(f"🟩 Se obtuvieron {len(datos)} filas desde la BD.")

        def inyectar_despues():
            print("🕓 Esperando a que cargue la página...")
            self.inyectar_tabla_todasllamadasxid(datos)

        # Espera 500ms después de la carga del HTML
        def on_load(ok):
            QTimer.singleShot(100, inyectar_despues)
            self.content_view.loadFinished.disconnect(on_load)

        self.content_view.load(url)
        self.content_view.loadFinished.connect(on_load)