from PyQt5.QtCore import QObject, Qt,pyqtSlot, QUrl, QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QFileDialog, QHBoxLayout,QFrame,QApplication, QSizePolicy, QSpacerItem
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
import json
import datetime
from src.db import *
from src.apis.transcripcion import *
from src.apis.gemini_api import *
from src.apis.nlp import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAGE_DIR = os.path.join(os.path.dirname(__file__), "gui")


class Bridge(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.datos_llamada_actual = None  # Aquí se asigna la llamada cargada
        self.login = None 
        

    @pyqtSlot(str)
    def cargar_pagina(self, nombre):
        """
        Recibe desde JavaScript el nombre lógico de la página
        y carga el HTML correspondiente según el tipo de usuario.
        """

        # Diccionario de páginas “lógicas” a archivos HTML
        rutas_admin = {
            "inicio": "inicio.html",
            "ejecutivos": "ejecutivos.html",
            "llamadas": "llamadas.html",
            "mi_cuenta": "mi_cuenta.html",
            "admin": "admin.html",
            "mensajes":"mensajes.html"
        }

        rutas_otros = {
            "inicio": "inicio_ejecutivo.html",
            "mis_llamadas": "mis_llamadas.html",
            "mensajes": "mensajes.html",
            "mi_cuenta": "mi_cuenta.html"
        }

        # 🔹 Determinar carpeta y rutas según el usuario
        if self.main_window.usuario == "admin":
            carpeta = "admin"
            rutas = rutas_admin
        else:
            carpeta = "otro"
            rutas = rutas_otros

        # 🔹 Verificar que el nombre exista en el diccionario correspondiente
        if nombre not in rutas:
            print(f"⚠️ Página desconocida o no permitida para este usuario: {nombre}")
            return

        archivo = rutas[nombre]
        path = os.path.join(PAGE_DIR, "pages", carpeta, archivo)

        # 🔹 Verificar que el archivo realmente exista
        if not os.path.exists(path):
            print(f"⚠️ Archivo no encontrado: {path}")
            return

        # 🔹 Cargar la página
        self.main_window.load_page(archivo)
        print(f"➡️ Cargando página: {archivo} para usuario: {self.main_window.usuario}")







    @pyqtSlot(str)
    def buscarLlamadaPorId(self, id_llamada):
        try:
            datos = obtener_llamada_por_id(id_llamada)
            if datos:
                self.main_window.inyectar_tabla_llamadas([datos])
            else:
                self.main_window.inyectar_tabla_llamadas([])
        except Exception as e:
            print("Error al buscar llamada por ID:", e)

    @pyqtSlot(str)
    def buscarEjecutivoPorId(self, id_ejecutivo):
        try:
            datos = obtener_ejecutivo_por_id(id_ejecutivo)
            if datos:
                self.main_window.inyectar_tabla_ejecutivos([datos])
            else:
                self.main_window.inyectar_tabla_ejecutivos([])
        except Exception as e:
            print("Error al buscar ejecutivo por ID:", e)


    @pyqtSlot()
    def volverTablaLlamadas(self):
        url = os.path.join(BASE_DIR, "gui","pages","admin", "llamadas.html")
        self.main_window.cargar_tabla_llamadas(QUrl.fromLocalFile(url))
    
    @pyqtSlot()
    def volverTablaLlamadasXejecutivo(self):
        url = os.path.join(BASE_DIR, "gui","pages","otro", "mis_llamadas.html")
        self.main_window.cargar_tabla_llamadasxid(QUrl.fromLocalFile(url))

    @pyqtSlot()
    def cerrarSesion(self):
        print("🔒 Sesión cerrada por el usuario")
        if self.main_window:
            self.main_window.close()



    @pyqtSlot(int)
    def verDetallesLlamada(self, id_llamada):
        self.main_window.cargar_detalle_llamada(id_llamada)

    @pyqtSlot(int)
    def verDetallesLlamadaXejecutivo(self, id_llamada):
        self.main_window.cargar_detalle_llamada_xejecutivo(id_llamada)
    
    @pyqtSlot()
    def abrir_agregar_ejecutivo(self):
        self.main_window.abrir_agregar_ejecutivo()

    @pyqtSlot()
    def actualizar_ranking_js(self):
        self.main_window.actualizar_ranking()

    @pyqtSlot(result=int)
    def obtener_cantidad_llamadas(self):
        return cantidad_llamadas()
    
    @pyqtSlot(result=int)
    def obtener_cantidad_llamadasxid(self):
        total = cantidad_llamadasxid(self.main_window.id_usuario)
        print(f"🔢 Total de llamadas encontradas: {total}")
        return total

    
    @pyqtSlot(result=float)
    def obtener_promedio_llamadas(self):
        total = promedio_llamadas(self.main_window.id_usuario)
        print(f"🔢 Promedio llamadas: {total}")
        return total

    @pyqtSlot()
    def abrir_editar_ejecutivo(self):
        self.main_window.abrir_editar_ejecutivo()

    @pyqtSlot()
    def abrir_editar_cliente(self):
        self.main_window.abrir_editar_cliente()

    @pyqtSlot()
    def abrir_eliminar_ejecutivo(self):
        self.main_window.abrir_eliminar_ejecutivo()

    @pyqtSlot()
    def abrir_agregar_cliente(self):
        self.main_window.abrir_agregar_cliente()

    @pyqtSlot()
    def abrir_eliminar_cliente(self):
        self.main_window.abrir_eliminar_cliente()


    @pyqtSlot()
    def abrir_agregar_supervisor(self):
        self.main_window.abrir_agregar_supervisor()

    @pyqtSlot()
    def abrir_eliminar_supervisor(self):
        self.main_window.abrir_eliminar_supervisor()

    @pyqtSlot()
    def abrir_editar_supervisor(self):
        self.main_window.abrir_editar_supervisor()


    
    @pyqtSlot()
    def abrir_agregar_llamada(self):
        self.main_window.abrir_agregar_llamada()

    @pyqtSlot()
    def abrir_eliminar_llamada(self):
        self.main_window.abrir_eliminar_llamada()

    @pyqtSlot(result='QVariantMap')
    def obtener_datos_usuario(self):
        return obtener_datos_usuario(self.main_window.id_usuario) or {}
    
    @pyqtSlot(result=int)
    def obtenerIdUsuario(self):
        """Devuelve el ID del usuario actualmente logueado"""
        try:
            return int(getattr(self.main_window, "id_usuario", 0))
        except (TypeError, ValueError):
            return 0


    @pyqtSlot(int, result=list)
    def obtenerConversacion(self, otro_usuario_id):
        from src.db import obtener_conversacion
        usuario_actual = self.main_window.id_usuario
        return obtener_conversacion(usuario_actual, otro_usuario_id, limit=200, asc=True)

    @pyqtSlot(int, str)
    def enviarMensaje(self, destinatario_id, texto):
        from src.db import guardar_mensaje
        usuario_actual = self.main_window.id_usuario
        guardar_mensaje(usuario_actual, destinatario_id, texto)

    @pyqtSlot(result=int)
    def contarMensajesNuevos(self):
        usuario = getattr(self.main_window, "id_usuario", None)
        if not usuario:
            return 0
        return contar_mensajes_no_leidos(usuario)

    @pyqtSlot(str)
    def marcarLeidosDe(self, otro_usuario):
        usuario = getattr(self.main_window, "id_usuario", None)
        if not usuario:
            return
        marcar_como_leido(usuario, otro_usuario)

    @pyqtSlot(result=list)
    def obtenerUsuarios(self):
        from src.db import obtener_usuarios
        usuario_actual = self.main_window.id_usuario
        return obtener_usuarios(excepto_id=usuario_actual)

    @pyqtSlot(result=int)
    def obtenerMensajesNoLeidos(self):
        usuario_id = getattr(self.main_window, "id_usuario", None)
        if not usuario_id:
            return 0
        return obtener_mensajes_no_leidos(usuario_id)

    @pyqtSlot(result='QVariantList')
    def obtenerUsuariosConMensajesNoLeidos(self):
        usuario_id = getattr(self.main_window, "id_usuario", None)
        if not usuario_id:
            return []
        return obtener_usuarios_con_mensajes_no_leidos(usuario_id)



    @pyqtSlot(int)
    def seleccionarAudio(self, id_llamada):
        # Abrir selector de archivo
        archivo, _ = QFileDialog.getOpenFileName(None, "Seleccionar audio", "", "Audio Files (*.mp3 *.wav)")
        if archivo:
            try:
                with open(archivo, "rb") as f:
                    contenido = f.read()
                conexion = conectar()
                cursor = conexion.cursor()
                sql = "UPDATE llamada SET audio_llamada=%s WHERE Id_Llamadas=%s"
                cursor.execute(sql, (contenido, id_llamada))
                conexion.commit()
                conexion.close()
                print(f"Audio subido correctamente para la llamada {id_llamada}")
            except Exception as e:
                print("Error al subir audio:", e)

    @pyqtSlot()
    def transcribirAudioActualAssemblyai(self):
        """Transcribe la llamada actual con Google y actualiza el HTML"""
        if not self.datos_llamada_actual or not self.datos_llamada_actual.get("audio_llamada"):
            self.enviarResultadoTranscripcion("⚠️ No hay audio cargado para transcribir")
            return

        try:
            audio_b64 = self.datos_llamada_actual["audio_llamada"]

                # 🔹 Mostrar mensaje inicial
            self.enviarResultadoTranscripcion("🔊 Transcribiendo audio… por favor espere")

            # 🔹 Crear y lanzar hilo
            self.thread_transcripcion = TranscripcionThread(audio_b64)
            
            # Conectar señales del hilo a tu función que actualiza HTML
            self.thread_transcripcion.resultado.connect(self.enviarResultadoTranscripcion)
            self.thread_transcripcion.error.connect(
                lambda e: self.enviarResultadoTranscripcion(f"⚠️ Error al transcribir: {e}")
            )
            
            # Iniciar hilo
            self.thread_transcripcion.start()

            # 🔹 Llamar a la función que transcribe
            texto = transcribir_audio_assemblyai(audio_b64, estado_callback=self.enviarResultadoTranscripcion)

            # 🔹 Mostrar resultado final
            self.enviarResultadoTranscripcion(texto)

        except Exception as e:
            self.enviarResultadoTranscripcion(f"⚠️ Error al transcribir el audio: {str(e)}")


    def enviarResultadoTranscripcion(self, texto):
        """Actualiza el HTML con el texto transcrito"""
        
        js = f'document.getElementById("resultadoTranscripcion").textContent = {json.dumps(texto)};'
        print("DEBUG: JS to run:", js[:200], "...")
        self.main_window.content_view.page().runJavaScript(js, lambda r: print("DEBUG: runJavaScript callback:", r))



    @pyqtSlot(str)
    def generarReporte(self, tipo):
        
        # --- CONSTANTES LOCALES (Colores de Marca para el diseño moderno) ---
        COLOR_PRIMARIO = colors.HexColor('#007ACC')       # Azul moderno para líneas y énfasis
        COLOR_TITULO = colors.HexColor('#333333')         # Gris oscuro para títulos principales
        COLOR_HEADER_BG = colors.HexColor('#F0F0F0')      # Fondo gris claro para el encabezado de la tabla

        # --- FUNCIÓN ANIDADA PARA CABECERA Y PIE DE PÁGINA ---
        # Esto da un toque moderno al documento (se ejecuta en cada página)
        def header_and_footer(canvas, doc):
            canvas.saveState()
            
            # 1. Cabecera (Línea de marca y título del documento)
            canvas.setStrokeColor(COLOR_PRIMARIO)
            canvas.setLineWidth(2)
            # Dibuja una línea de color primario en la parte superior
            canvas.line(doc.leftMargin, doc.height + doc.topMargin - 15, doc.width + doc.leftMargin, doc.height + doc.topMargin - 15)
            
            # Título en la cabecera (derecha)
            ptext = "Reporte Generado: {}".format(doc.title)
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(colors.gray)
            canvas.drawString(doc.width + doc.leftMargin - 120, doc.height + doc.topMargin - 30, ptext)


            # 2. Pie de página (Número de página centrado)
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(colors.gray)
            page_num = canvas.getPageNumber()
            text = "Página %s" % page_num
            canvas.drawCentredString(doc.width / 2 + doc.leftMargin, 0.75 * inch, text)
            
            canvas.restoreState()

        # ------------------------------------------------------------------
        # --- INICIO DE LA LÓGICA PRINCIPAL DEL REPORTE ---
        # ------------------------------------------------------------------
        print(f"🧾 Generando reporte de tipo: {tipo}")

        # 🗂️ Abrir ventana de “Guardar como”
        ruta_archivo, _ = QFileDialog.getSaveFileName(
            None,
            "Guardar reporte como...",
            f"reporte_{tipo}.pdf",
            "Archivos PDF (*.pdf)"
        )

        if not ruta_archivo:  # Si el usuario cancela
            print("❌ Generación de reporte cancelada por el usuario.")
            return

        # --- Selección de datos ---
        if tipo == "llamadas":
            # CONEXIÓN ORIGINAL: obtener_llamadas_reporte()
            resultados = obtener_llamadas_reporte() 
            titulo = "📞 Reporte de Llamadas"
        elif tipo == "clientes":
            # CONEXIÓN ORIGINAL: obtener_clientes_reporte()
            resultados = obtener_clientes_reporte()
            titulo = "👤 Reporte de Clientes"
        elif tipo == "ejecutivos":
            # CONEXIÓN ORIGINAL: obtener_ejecutivos_reporte()
            resultados = obtener_ejecutivos_reporte()
            titulo = "💼 Reporte de Ejecutivos"
        else:
            print("❌ Tipo de reporte no reconocido.")
            return

        # --- Configuración del Documento ---
        doc = SimpleDocTemplate(
            ruta_archivo, 
            pagesize=A4,
            leftMargin=0.75 * inch,    # Márgenes ajustados
            rightMargin=0.75 * inch,
            topMargin=1.2 * inch,      # Aumentado para el header
            bottomMargin=0.75 * inch
        )
        doc.title = titulo # Añadir título para el header_and_footer

        styles = getSampleStyleSheet()
        contenido = []
        
        # 1. Definir Estilo de Título Moderno (Reemplaza styles["Title"])
        styles.add(ParagraphStyle(
            name='ModernTitle',
            parent=styles['Title'],
            fontSize=20,
            leading=24,
            textColor=COLOR_TITULO,
            fontName='Helvetica-Bold', # Fuente más moderna
            alignment=1 # Centrado
        ))

        # 2. Agregar Título Principal
        contenido.append(Paragraph(titulo, styles["ModernTitle"]))
        contenido.append(Spacer(1, 24))

        # --- Armar tabla ---
        if resultados:
            columnas = list(resultados[0].keys())
            filas = [columnas] + [list(r.values()) for r in resultados]
        else:
            # Manejo de "Sin datos" con el estilo normal, asegurando que se construya el PDF con header/footer
            contenido.append(Paragraph("Sin datos disponibles para el reporte.", styles["Normal"]))
            doc.build(contenido, onFirstPage=header_and_footer, onLaterPages=header_and_footer)
            print(f"✅ Reporte guardado correctamente en: {ruta_archivo}")
            return


        # 3. Crear Tabla con Estilo Moderno
        tabla = Table(filas)
        
        # Estilo de tabla mejorado: limpio, contrastado y profesional
        tabla.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0,0), (-1,0), COLOR_HEADER_BG), # Fondo gris claro
            ('TEXTCOLOR', (0,0), (-1,0), COLOR_TITULO),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('TOPPADDING', (0,0), (-1,0), 12),

            # Datos
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            
            # Alineación y Espaciado
            ('ALIGN', (0,0), (-1,0), 'CENTER'),      # Encabezado centrado
            ('ALIGN', (0,1), (-1,-1), 'LEFT'),       # Datos alineados a la izquierda para mejor lectura
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            
            # Grilla fina y sutil
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')), 
        ]))
        
        contenido.append(tabla)

        # 4. Construir el documento con la cabecera/pie modernos
        doc.build(contenido, onFirstPage=header_and_footer, onLaterPages=header_and_footer)
        
        print(f"✅ Reporte guardado correctamente en: {ruta_archivo}")


class TranscripcionThread(QThread):
    # Señal que emitirá el texto final
    resultado = pyqtSignal(str)
    # Señal que emitirá un error si ocurre
    error = pyqtSignal(str)

    def __init__(self, audio_b64):
        super().__init__()
        self.audio_b64 = audio_b64

    def run(self):
        """Este código se ejecuta en un hilo separado"""
        try:
            # Llamamos a la función de Google
            texto = transcribir_audio_assemblyai(self.audio_b64)
            # Emitimos el resultado para actualizar el HTML
            self.resultado.emit(texto)
        except Exception as e:
            self.error.emit(str(e))

#<-------AGREGAR EJECUTIVO--------->


class AgregarEjecutivoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("➕ Agregar Ejecutivo")
        self.setFixedSize(400, 650)
        self.setWindowIcon(QIcon("assets/logos/transparente.png"))

        self.setStyleSheet("""
            QDialog {
                background-color: #3f3f3f;
                color: #E0E1DD;
                font-family: 'Segoe UI';
                border-radius: 18px;
            }
            QLabel {
                background: transparent;
                font-size: 13px;
                font-weight: 600;
                color: #E0E1DD;
                margin-top: 6px;
            }
            QLineEdit, QComboBox {
                background: #8b8b8b;
                color: #E0E1DD;
                border: 1px solid #3f3f3f;
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #E0E1DD;
                background: #8b8b8b;
            }
            QPushButton {
                background-color: #8b8b8b;
                color: #E0E1DD;
                border: none;
                border-radius: 10px;
                padding: 12px 0;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #a0a0a0;
            }
            QPushButton:pressed {
                background-color: #707070;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("Agregar nuevo ejecutivo")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #E0E1DD; margin-bottom: 10px;")
        main_layout.addWidget(titulo)

        self.inputs = {}
        campos = [
            ("RUT (sin dígito)", "rut_input"),
            ("Dígito Verificador", "dv_input"),
            ("Nombre", "nombre_input"),
            ("Apellido", "apellido_input"),
        ]

        for etiqueta, nombre_campo in campos:
            label = QLabel(etiqueta)
            input_field = QLineEdit()
            main_layout.addWidget(label)
            main_layout.addWidget(input_field)
            self.inputs[nombre_campo] = input_field

        main_layout.addWidget(QLabel("Cargo"))
        self.rol_select = QComboBox()
        self.rol_select.addItems(["SOP1", "SOP2", "SOP3"])
        main_layout.addWidget(self.rol_select)

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        self.guardar_btn = QPushButton("Agregar Ejecutivo")
        self.guardar_btn.setFixedWidth(220)
        self.guardar_btn.clicked.connect(self.agregar_ejecutivo)
        btn_layout.addWidget(self.guardar_btn)
        main_layout.addLayout(btn_layout)


    # -------------------------------------------------
    # 💾 Lógica para agregar el ejecutivo a la BD
    # -------------------------------------------------
    def agregar_ejecutivo(self):
        rut = self.inputs["rut_input"].text().strip()
        dv = self.inputs["dv_input"].text().strip()
        nombre = self.inputs["nombre_input"].text().strip()
        apellido = self.inputs["apellido_input"].text().strip()
        rol = self.rol_select.currentText()

        # Validar campos obligatorios
        if not rut or not dv or not nombre or not apellido:
            QMessageBox.warning(self, "Error", "Debe ingresar RUT, dígito, nombre y apellido.")
            return

        # Validar que el RUT sea numérico
        if not rut.isdigit():
            QMessageBox.warning(self, "Error", "El RUT debe contener solo números (sin puntos ni guion).")
            return

        try:
            agregar_ejecutivo(rut, dv, nombre, apellido, rol)
            QMessageBox.information(self, "Éxito", f"Ejecutivo {nombre} agregado correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar: {e}")








#<-------EDITAR EJECUTIVO--------->


class EditarEjecutivoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("✏️ Editar Ejecutivo")
        self.resize(520, 520)
        self.setWindowIcon(QIcon("assets/logos/transparente.png"))

        self.setStyleSheet("""
            QDialog { background-color: #3f3f3f; color: #E0E1DD; font-family: 'Segoe UI'; }
            QLabel { background: transparent; color: #E0E1DD; font-size: 13px; font-weight: 600; margin-top: 6px; }
            QLineEdit, QComboBox {
                background: #8b8b8b;
                border: 1px solid #3f3f3f;
                border-radius: 8px;
                color: #E0E1DD;
                padding: 8px 10px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #E0E1DD;
                background: #8b8b8b;
            }
            QPushButton {
                background-color: #8b8b8b;
                border: none;
                color: #E0E1DD;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #a0a0a0; }
            QPushButton:pressed { background-color: #707070; }
            QFrame#line {
                background-color: #8b8b8b;
                max-height: 1px;
                min-height: 1px;
                margin: 10px 0;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Editar Información de Ejecutivo")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addWidget(QLabel("Buscar por ID del Ejecutivo"))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Ej: 102")
        layout.addWidget(self.id_input)

        self.buscar_btn = QPushButton("🔎 Buscar Ejecutivo")
        self.buscar_btn.clicked.connect(self.buscar_ejecutivo)
        layout.addWidget(self.buscar_btn)

        line = QFrame()
        line.setObjectName("line")
        layout.addWidget(line)

        layout.addWidget(QLabel("RUT"))
        self.rut_input = QLineEdit()
        layout.addWidget(self.rut_input)

        layout.addWidget(QLabel("Dígito Verificador"))
        self.dv_input = QLineEdit()
        layout.addWidget(self.dv_input)

        layout.addWidget(QLabel("Nombre"))
        self.nombre_input = QLineEdit()
        layout.addWidget(self.nombre_input)

        layout.addWidget(QLabel("Apellido"))
        self.apellido_input = QLineEdit()
        layout.addWidget(self.apellido_input)

        layout.addWidget(QLabel("Tipo de Cargo"))
        self.cargo_input = QComboBox()
        self.cargo_input.addItems(["SOP1", "SOP2", "SOP3"])
        layout.addWidget(self.cargo_input)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.setStyleSheet("""
            QPushButton {
                background-color: #3f3f3f;
                color: #E0E1DD;
                border-radius: 8px;
                padding: 10px 16px;
            }
            QPushButton:hover { background-color: #5a5a5a; }
        """)
        cancelar_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancelar_btn)

        self.guardar_btn = QPushButton("💾 Guardar Cambios")
        self.guardar_btn.clicked.connect(self.guardar_cambios)
        btn_layout.addWidget(self.guardar_btn)

        layout.addItem(QSpacerItem(10, 15, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addLayout(btn_layout)
        self.setLayout(layout)




    def buscar_ejecutivo(self):
        id_ejecutivo = self.id_input.text().strip()
        if not id_ejecutivo:
            QMessageBox.warning(self, "Error", "Debe ingresar un ID válido.")
            return

        try:
            datos = obtener_ejecutivo_por_id(id_ejecutivo)
            if datos:
                self.rut_input.setText(str(datos["Rut_Ejecutivo"]))
                self.dv_input.setText(str(datos["Digito_Verificador"]))
                self.nombre_input.setText(str(datos["Nombre_Ejecutivo"]))
                self.apellido_input.setText(str(datos["Apellido_Ejecutivo"]))
                self.cargo_input.setCurrentText(str(datos["TCARGO_Id_Tipo_Cargo"]))
            else:
                QMessageBox.warning(self, "Sin resultados", "No se encontró ningún ejecutivo con ese ID.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo buscar: {e}")

    def guardar_cambios(self):
        id_ejecutivo = self.id_input.text().strip()
        rut = self.rut_input.text().strip()
        digito = self.dv_input.text().strip()
        nombre = self.nombre_input.text().strip()
        apellido = self.apellido_input.text().strip()
        cargo = self.cargo_input.currentText().strip()

        if not id_ejecutivo or not rut or not digito or not nombre or not apellido:
            QMessageBox.warning(self, "Error", "Debe completar todos los campos antes de guardar.")
            return

        try:
            actualizar_ejecutivo(id_ejecutivo, rut, digito, nombre, apellido, cargo)
            QMessageBox.information(self, "Éxito", "Datos actualizados correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar: {e}")




#<-------ELIMINAR EJECUTIVO--------->




class EliminarEjecutivoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🗑️ Eliminar Ejecutivo")
        self.resize(420, 280)
        self.setWindowIcon(QIcon("assets/logos/transparente.png"))

        self.setStyleSheet("""
            QDialog { background-color: #3f3f3f; color: #E0E1DD; font-family: 'Segoe UI'; }
            QLabel { background: transparent; font-size: 13px; font-weight: 600; color: #E0E1DD; margin-top: 6px; }
            QLineEdit { background: #8b8b8b; color: #E0E1DD; border: 1px solid #3f3f3f; border-radius: 8px; padding: 8px 10px; font-size: 13px; }
            QLineEdit:focus { border: 1px solid #E0E1DD; background: #8b8b8b; }
            QPushButton { background-color: #8b8b8b; border: none; color: #E0E1DD; font-weight: bold; border-radius: 10px; padding: 10px 16px; font-size: 14px; }
            QPushButton:hover { background-color: #a0a0a0; }
            QPushButton:pressed { background-color: #707070; }
            QLabel#info_label { font-size: 13px; color: #E0E1DD; margin-top: 8px; }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Eliminar Información de Ejecutivo")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addWidget(QLabel("Buscar por ID del Ejecutivo"))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Ej: 102")
        layout.addWidget(self.id_input)

        self.buscar_btn = QPushButton("🔎 Buscar Ejecutivo")
        self.buscar_btn.clicked.connect(self.buscar_ejecutivo)
        layout.addWidget(self.buscar_btn)

        self.info_label = QLabel("")
        self.info_label.setObjectName("info_label")
        self.info_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.info_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.setStyleSheet("""
            QPushButton { background-color: #3f3f3f; color: #E0E1DD; border-radius: 8px; padding: 10px 16px; }
            QPushButton:hover { background-color: #5a5a5a; }
        """)
        cancelar_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancelar_btn)

        self.eliminar_btn = QPushButton("🗑️ Eliminar Ejecutivo")
        self.eliminar_btn.clicked.connect(self.eliminar_ejecutivo)
        self.eliminar_btn.setEnabled(False)
        btn_layout.addWidget(self.eliminar_btn)

        layout.addItem(QSpacerItem(10, 15, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addLayout(btn_layout)
        self.setLayout(layout)



    def buscar_ejecutivo(self):
        id_ejecutivo = self.id_input.text().strip()
        if not id_ejecutivo:
            QMessageBox.warning(self, "Error", "Debe ingresar un ID válido.")
            return

        try:
            datos = obtener_ejecutivo_por_id(id_ejecutivo)
            if datos:
                self.info_label.setText(
                    f"Nombre: {datos['Nombre_Ejecutivo']} {datos['Apellido_Ejecutivo']}\n"
                    f"Rut: {datos['Rut_Ejecutivo']}-{datos['Digito_Verificador']}\n"
                    f"Rol: {datos['TCARGO_Id_Tipo_Cargo']}"
                )
                self.eliminar_btn.setEnabled(True)
            else:
                QMessageBox.warning(self, "Sin resultados", "No se encontró ningún ejecutivo con ese ID.")
                self.info_label.setText("")
                self.eliminar_btn.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo buscar: {e}")

    def eliminar_ejecutivo(self):
        id_ejecutivo = self.id_input.text().strip()
        if not id_ejecutivo:
            return

        confirmar = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Estás seguro de eliminar el ejecutivo con ID {id_ejecutivo}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmar == QMessageBox.No:
            return

        try:
            eliminar_ejecutivo(id_ejecutivo)
            QMessageBox.information(self, "Éxito", "Ejecutivo eliminado correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")



#<-------------------AGREGAR CLIENTE--------------------->

class AgregarClienteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("➕ Agregar Cliente")
        self.setFixedSize(400, 650)
        self.setWindowIcon(QIcon("assets/logos/transparente.png"))

        self.setStyleSheet("""
            QDialog { background-color: #3f3f3f; border-radius: 18px; color: #E0E1DD; font-family: 'Segoe UI'; }
            QLabel { background: transparent; font-size: 13px; font-weight: 600; color: #8b8b8b; margin-top: 6px; }
            QLineEdit, QComboBox {
                background: transparent; color: #E0E1DD; border: 1px solid #8b8b8b;
                border-radius: 8px; padding: 8px 10px; font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #E0E1DD; background: transparent; }
            QPushButton {
                background-color: #8b8b8b; color: #3f3f3f; border: none;
                border-radius: 10px; padding: 12px 0; font-weight: bold; font-size: 15px;
            }
            QPushButton:hover { background-color: #E0E1DD; color: #3f3f3f; }
            QPushButton:pressed { background-color: #3f3f3f; color: #E0E1DD; border: 1px solid #E0E1DD; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("Agregar nuevo cliente")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #E0E1DD; font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(titulo)

        self.inputs = {}
        campos = [
            ("Rut", "rut_input"),
            ("Dígito Verificador", "dv_input"),
            ("Nombre", "nombre_input"),
            ("Apellido", "apellido_input"),
        ]
        for etiqueta, nombre_campo in campos:
            label = QLabel(etiqueta)
            input_field = QLineEdit()
            main_layout.addWidget(label)
            main_layout.addWidget(input_field)
            self.inputs[nombre_campo] = input_field

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        self.guardar_btn = QPushButton("Agregar Cliente")
        self.guardar_btn.setFixedWidth(220)
        self.guardar_btn.clicked.connect(self.agregar_cliente)
        btn_layout.addWidget(self.guardar_btn)
        main_layout.addLayout(btn_layout)


    def agregar_cliente(self):
        rut = self.inputs["rut_input"].text().strip()
        dv = self.inputs["dv_input"].text().strip()
        nombre = self.inputs["nombre_input"].text().strip()
        apellido = self.inputs["apellido_input"].text().strip()

        if not rut or not dv or not nombre or not apellido:
            QMessageBox.warning(self, "Error", "Debe completar todos los campos.")
            return

        try:
            agregar_cliente(rut, dv, nombre, apellido)
            QMessageBox.information(self, "Éxito", f"Cliente {nombre} agregado correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar: {e}")



class EditarClienteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("✏️ Editar Cliente")
        self.resize(520, 520)
        self.setWindowIcon(QIcon("assets/logos/transparente.png"))

        self.setStyleSheet("""
            QDialog { background-color: #3f3f3f; color: #E0E1DD; font-family: 'Segoe UI'; }
            QLabel { background: transparent; color: #E0E1DD; font-size: 13px; font-weight: 600; margin-top: 6px; }
            QLineEdit, QComboBox {
                background: #8b8b8b;
                border: 1px solid #3f3f3f;
                border-radius: 8px;
                color: #E0E1DD;
                padding: 8px 10px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #E0E1DD;
                background: #8b8b8b;
            }
            QPushButton {
                background-color: #8b8b8b;
                border: none;
                color: #E0E1DD;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #a0a0a0; }
            QPushButton:pressed { background-color: #707070; }
            QFrame#line {
                background-color: #8b8b8b;
                max-height: 1px;
                min-height: 1px;
                margin: 10px 0;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Editar Información de Cliente")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addWidget(QLabel("Buscar por ID del Cliente"))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Ej: 102")
        layout.addWidget(self.id_input)

        self.buscar_btn = QPushButton("🔎 Buscar Cliente")
        self.buscar_btn.clicked.connect(self.buscar_ejecutivo)
        layout.addWidget(self.buscar_btn)

        line = QFrame()
        line.setObjectName("line")
        layout.addWidget(line)

        layout.addWidget(QLabel("RUT"))
        self.rut_input = QLineEdit()
        layout.addWidget(self.rut_input)

        layout.addWidget(QLabel("Dígito Verificador"))
        self.dv_input = QLineEdit()
        layout.addWidget(self.dv_input)

        layout.addWidget(QLabel("Nombre"))
        self.nombre_input = QLineEdit()
        layout.addWidget(self.nombre_input)

        layout.addWidget(QLabel("Apellido"))
        self.apellido_input = QLineEdit()
        layout.addWidget(self.apellido_input)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.setStyleSheet("""
            QPushButton {
                background-color: #3f3f3f;
                color: #E0E1DD;
                border-radius: 8px;
                padding: 10px 16px;
            }
            QPushButton:hover { background-color: #5a5a5a; }
        """)
        cancelar_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancelar_btn)

        self.guardar_btn = QPushButton("💾 Guardar Cambios")
        self.guardar_btn.clicked.connect(self.guardar_cambios)
        btn_layout.addWidget(self.guardar_btn)

        layout.addItem(QSpacerItem(10, 15, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addLayout(btn_layout)
        self.setLayout(layout)




    def buscar_ejecutivo(self):
        id_ejecutivo = self.id_input.text().strip()
        if not id_ejecutivo:
            QMessageBox.warning(self, "Error", "Debe ingresar un ID válido.")
            return

        try:
            datos = obtener_cliente_por_id(id_ejecutivo)
            if datos:
                self.rut_input.setText(str(datos["Rut_Cliente"]))
                self.dv_input.setText(str(datos["Digito_Verificador"]))
                self.nombre_input.setText(str(datos["Nombre_Cliente"]))
                self.apellido_input.setText(str(datos["Apellido_Cliente"]))
            else:
                QMessageBox.warning(self, "Sin resultados", "No se encontró ningún ejecutivo con ese ID.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo buscar: {e}")

    def guardar_cambios(self):
        id_ejecutivo = self.id_input.text().strip()
        rut = self.rut_input.text().strip()
        digito = self.dv_input.text().strip()
        nombre = self.nombre_input.text().strip()
        apellido = self.apellido_input.text().strip()

        if not id_ejecutivo or not rut or not digito or not nombre or not apellido:
            QMessageBox.warning(self, "Error", "Debe completar todos los campos antes de guardar.")
            return

        try:
            actualizar_cliente(id_ejecutivo, rut, digito, nombre, apellido)
            QMessageBox.information(self, "Éxito", "Datos actualizados correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar: {e}")







class EliminarClienteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🗑️ Eliminar Cliente")
        self.resize(420, 280)
        self.setWindowIcon(QIcon("assets/logos/transparente.png"))

        self.setStyleSheet("""
            QDialog { background-color: #3f3f3f; color: #E0E1DD; font-family: 'Segoe UI'; }
            QLabel { background: transparent; font-size: 13px; font-weight: 600; color: #8b8b8b; margin-top: 6px; }
            QLineEdit { background: transparent; color: #E0E1DD; border: 1px solid #8b8b8b; border-radius: 8px; padding: 8px 10px; font-size: 13px; }
            QLineEdit:focus { border: 1px solid #E0E1DD; background: transparent; }
            QPushButton { background-color: #8b8b8b; border: none; color: #3f3f3f; font-weight: bold; border-radius: 10px; padding: 10px 16px; font-size: 14px; }
            QPushButton:hover { background-color: #E0E1DD; color: #3f3f3f; }
            QPushButton:pressed { background-color: #3f3f3f; color: #E0E1DD; border: 1px solid #E0E1DD; }
            QLabel#info_label { font-size: 13px; color: #E0E1DD; margin-top: 8px; }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Eliminar Información de Cliente")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addWidget(QLabel("Buscar por ID del Cliente"))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Ej: 205")
        layout.addWidget(self.id_input)

        self.buscar_btn = QPushButton("🔎 Buscar Cliente")
        self.buscar_btn.clicked.connect(self.buscar_cliente)
        layout.addWidget(self.buscar_btn)

        self.info_label = QLabel("")
        self.info_label.setObjectName("info_label")
        self.info_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.info_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.setStyleSheet("""
            QPushButton { background-color: #8b8b8b; color: #3f3f3f; border-radius: 8px; padding: 10px 16px; }
            QPushButton:hover { background-color: #E0E1DD; color: #3f3f3f; }
        """)
        cancelar_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancelar_btn)

        self.eliminar_btn = QPushButton("🗑️ Eliminar Cliente")
        self.eliminar_btn.clicked.connect(self.eliminar_cliente)
        self.eliminar_btn.setEnabled(False)
        btn_layout.addWidget(self.eliminar_btn)

        layout.addItem(QSpacerItem(10, 15, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addLayout(btn_layout)
        self.setLayout(layout)


    def buscar_cliente(self):
        id_cliente = self.id_input.text().strip()
        if not id_cliente:
            QMessageBox.warning(self, "Error", "Debe ingresar un ID válido.")
            return

        try:
            datos = obtener_cliente_por_id(id_cliente)
            if datos:
                self.info_label.setText(
                    f"Nombre: {datos['Nombre_Cliente']} {datos['Apellido_Cliente']}\n"
                    f"RUT: {datos['Rut_Cliente']}-{datos['Digito_Verificador']}"
                )
                self.eliminar_btn.setEnabled(True)
            else:
                QMessageBox.warning(self, "Sin resultados", "No se encontró ningún cliente con ese ID.")
                self.info_label.setText("")
                self.eliminar_btn.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo buscar: {e}")

    def eliminar_cliente(self):
        id_cliente = self.id_input.text().strip()
        if not id_cliente:
            return

        confirmar = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Estás seguro de eliminar el cliente con ID {id_cliente}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmar == QMessageBox.No:
            return

        try:
            eliminar_cliente(id_cliente)
            QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")






class AgregarLlamadaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📞 Agregar Llamada")
        self.setFixedSize(420, 680)
        self.setWindowIcon(QIcon("assets/logos/transparente.png"))

        # 🎨 Paleta aplicada
        self.setStyleSheet("""
            QDialog { background-color: #3f3f3f; color: #E0E1DD; font-family: 'Segoe UI'; border-radius: 18px; }
            QLabel { background: transparent; font-size: 13px; font-weight: 600; color: #8b8b8b; margin-top: 6px; }
            QLineEdit { background: transparent; color: #E0E1DD; border: 1px solid #8b8b8b; border-radius: 8px; padding: 8px 10px; font-size: 13px; }
            QLineEdit:focus { border: 1px solid #E0E1DD; background: transparent; }
            QPushButton {
                background-color: #8b8b8b;
                color: #3f3f3f;
                border: none;
                border-radius: 10px;
                padding: 12px 0;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #E0E1DD;
                color: #3f3f3f;
            }
            QPushButton:pressed {
                background-color: #3f3f3f;
                color: #E0E1DD;
                border: 1px solid #E0E1DD;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(30, 30, 30, 30)

        # Título
        title = QLabel("Agregar nueva llamada")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #E0E1DD;")
        layout.addWidget(title)

        # Campos de IDs
        self.inputs = {}
        campos = [
            ("ID Ejecutivo", "id_ejecutivo"),
            ("ID Cliente", "id_cliente"),
            ("ID Supervisor", "id_supervisor"),
        ]

        for etiqueta, campo in campos:
            lbl = QLabel(etiqueta)
            entrada = QLineEdit()
            entrada.setPlaceholderText(f"{etiqueta}")
            layout.addWidget(lbl)
            layout.addWidget(entrada)
            self.inputs[campo] = entrada

        # Subir audio
        self.audio_path = None
        audio_label = QLabel("Archivo de audio de la llamada")
        self.audio_btn = QPushButton("🎵 Seleccionar archivo")
        self.audio_btn.clicked.connect(self.seleccionar_audio)
        self.audio_name = QLabel("Ningún archivo seleccionado")
        self.audio_name.setStyleSheet("font-size: 12px; color: #8b8b8b;")

        layout.addWidget(audio_label)
        layout.addWidget(self.audio_btn)
        layout.addWidget(self.audio_name)

        # Fecha y hora
        fecha_hora_actual = datetime.datetime.now()
        self.fecha_hora_label = QLabel(f"Fecha y hora actual: {fecha_hora_actual}")
        self.fecha_hora_label.setStyleSheet("font-size: 12px; color: #8b8b8b; margin-top: 10px;")
        layout.addWidget(self.fecha_hora_label)

        # Botón guardar
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        self.guardar_btn = QPushButton("Agregar Llamada")
        self.guardar_btn.setFixedWidth(220)
        self.guardar_btn.clicked.connect(self.agregar_llamada)
        btn_layout.addWidget(self.guardar_btn)
        layout.addLayout(btn_layout)

        layout.addItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))


    # --------------------- Métodos internos ---------------------

    def seleccionar_audio(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar audio", "", "Archivos de audio (*.mp3 *.wav *.m4a)")
        if ruta:
            self.audio_path = ruta
            nombre = os.path.basename(ruta)
            self.audio_name.setText(f"Seleccionado: {nombre}")
        else:
            self.audio_name.setText("Ningún archivo seleccionado")

    def agregar_llamada(self):
        """Recoge los datos del formulario, procesa el audio y guarda la llamada"""
        id_ejecutivo = self.inputs["id_ejecutivo"].text().strip()
        id_cliente = self.inputs["id_cliente"].text().strip()
        id_supervisor = self.inputs["id_supervisor"].text().strip()
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hora = fecha

        if not all([id_ejecutivo, id_cliente, id_supervisor, self.audio_path]):
            QMessageBox.warning(self, "Error", "Debe completar todos los campos y seleccionar un audio.")
            return

        try:
            # ----------------- Procesamiento completo dentro de la clase -----------------
            # Leer audio
            with open(self.audio_path, "rb") as f:
                audio_data = f.read()

            # Base64 para transcripción
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")

            # Transcribir
            transcripcion = transcribir_audio_assemblyai(audio_base64)

            # Evaluar NLP y Gemini
            score_nlp = analizar_sentimiento(transcripcion)
            score_gemini = consultar_gemini(transcripcion)

            score_final = round((score_nlp + score_gemini)/2)
            score_final = max(1, min(7, score_final))

            # Insertar en la base de datos
            conn = conectar()
            cursor = conn.cursor()
            query = """
                INSERT INTO llamada
                (Fecha, Hora, EJECUTIVO_Id_ejecutivo, CLIENTE_Id_cliente, SUPERVISOR_Id_Supervisor,
                 CLASIFI_LLAMADA_Id_Clasifi_Llam, audio_llamada)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (fecha, hora, id_ejecutivo, id_cliente, id_supervisor,
                                   score_final, audio_data))
            conn.commit()
            nuevo_id = cursor.lastrowid
            cursor.close()
            conn.close()

            QMessageBox.information(self, "Éxito", f"Llamada registrada correctamente con ID {nuevo_id}.")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo registrar la llamada: {e}")
#<---------------ELIMINAR LLAMADA------------------>

class EliminarLlamadaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🗑️ Eliminar Llamada")
        self.resize(420, 280)
        self.setWindowIcon(QIcon("assets/logos/transparente.png"))

        # 🎨 Paleta aplicada
        self.setStyleSheet("""
            QDialog {
                background-color: #3f3f3f;  /* fondo oscuro */
                color: #E0E1DD;  /* texto claro */
                font-family: 'Segoe UI';
            }
            QLabel {
                background: transparent;
                font-size: 13px;
                font-weight: 600;
                color: #8b8b8b;  /* texto secundario */
                margin-top: 6px;
            }
            QLineEdit {
                background: #8b8b8b;  /* fondo claro */
                color: #3f3f3f;  /* texto oscuro */
                border: 1px solid #E0E1DD;
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #E0E1DD;
                background: #E0E1DD;
                color: #3f3f3f;
            }
            QPushButton {
                background-color: #8b8b8b;
                border: none;
                color: #3f3f3f;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #E0E1DD;
                color: #3f3f3f;
            }
            QPushButton:pressed {
                background-color: #3f3f3f;
                color: #E0E1DD;
                border: 1px solid #E0E1DD;
            }
            QLabel#info_label {
                font-size: 13px;
                color: #E0E1DD;
                margin-top: 8px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Eliminar Información de Llamada")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addWidget(QLabel("Buscar por ID de la Llamada"))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Ej: 205")
        layout.addWidget(self.id_input)

        self.buscar_btn = QPushButton("🔎 Buscar Llamada")
        self.buscar_btn.clicked.connect(self.buscar_llamada)
        layout.addWidget(self.buscar_btn)

        self.info_label = QLabel("")
        self.info_label.setObjectName("info_label")
        self.info_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.info_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.setStyleSheet("""
            QPushButton {
                background-color: #3f3f3f;
                color: #E0E1DD;
                border: 1px solid #8b8b8b;
                border-radius: 8px;
                padding: 10px 16px;
            }
            QPushButton:hover {
                background-color: #8b8b8b;
                color: #3f3f3f;
            }
        """)
        cancelar_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancelar_btn)

        self.eliminar_btn = QPushButton("🗑️ Eliminar Llamada")
        self.eliminar_btn.clicked.connect(self.eliminar_llamada)
        self.eliminar_btn.setEnabled(False)
        btn_layout.addWidget(self.eliminar_btn)

        layout.addItem(QSpacerItem(10, 15, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def buscar_llamada(self):
        id_llamada = self.id_input.text().strip()
        if not id_llamada:
            QMessageBox.warning(self, "Error", "Debe ingresar un ID válido.")
            return

        try:
            datos = obtener_llamada_por_id(id_llamada)
            if datos:
                self.info_label.setText(
                    f"Fecha: {datos['Fecha']}\n"
                    f"Hora: {datos['Hora']}\n"
                    f"Ejecutivo ID: {datos['EJECUTIVO_Id_ejecutivo']}\n"
                    f"Cliente ID: {datos['CLIENTE_Id_cliente']}"
                )
                self.eliminar_btn.setEnabled(True)
            else:
                QMessageBox.warning(self, "Sin resultados", "No se encontró ninguna llamada con ese ID.")
                self.info_label.setText("")
                self.eliminar_btn.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo buscar: {e}")

    def eliminar_llamada(self):
        id_llamada = self.id_input.text().strip()
        if not id_llamada:
            return

        confirmar = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Estás seguro de eliminar la llamada con ID {id_llamada}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmar == QMessageBox.No:
            return

        try:
            eliminar_llamada(id_llamada)
            QMessageBox.information(self, "Éxito", "Llamada eliminada correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")

#-------------------------------- SUPERVISOR-------------------------------------------------
class AgregarSupervisorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("➕ Agregar Supervisor")
        self.setFixedSize(400, 650)
        self.setWindowIcon(QIcon("assets/logos/transparente.png"))

        self.setStyleSheet("""
            QDialog { background-color: #3f3f3f; border-radius: 18px; color: #E0E1DD; font-family: 'Segoe UI'; }
            QLabel { background: transparent; font-size: 13px; font-weight: 600; color: #8b8b8b; margin-top: 6px; }
            QLineEdit, QComboBox {
                background: transparent; color: #E0E1DD; border: 1px solid #8b8b8b;
                border-radius: 8px; padding: 8px 10px; font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #E0E1DD; background: transparent; }
            QPushButton {
                background-color: #8b8b8b; color: #3f3f3f; border: none;
                border-radius: 10px; padding: 12px 0; font-weight: bold; font-size: 15px;
            }
            QPushButton:hover { background-color: #E0E1DD; color: #3f3f3f; }
            QPushButton:pressed { background-color: #3f3f3f; color: #E0E1DD; border: 1px solid #E0E1DD; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("Agregar nuevo supervisor")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #E0E1DD; font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(titulo)

        self.inputs = {}
        campos = [
            ("Rut", "rut_input"),
            ("Dígito Verificador", "dv_input"),
            ("Nombre", "nombre_input"),
            ("Apellido", "apellido_input"),
        ]
        for etiqueta, nombre_campo in campos:
            label = QLabel(etiqueta)
            input_field = QLineEdit()
            main_layout.addWidget(label)
            main_layout.addWidget(input_field)
            self.inputs[nombre_campo] = input_field

        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        self.guardar_btn = QPushButton("Agregar Supervisor")
        self.guardar_btn.setFixedWidth(220)
        self.guardar_btn.clicked.connect(self.agregar_supervisor)
        btn_layout.addWidget(self.guardar_btn)
        main_layout.addLayout(btn_layout)

    def agregar_supervisor(self):
        rut = self.inputs["rut_input"].text().strip()
        dv = self.inputs["dv_input"].text().strip()
        nombre = self.inputs["nombre_input"].text().strip()
        apellido = self.inputs["apellido_input"].text().strip()

        if not rut or not dv or not nombre or not apellido:
            QMessageBox.warning(self, "Error", "Debe completar todos los campos.")
            return

        try:
            agregar_supervisor(rut, dv, nombre, apellido)
            QMessageBox.information(self, "Éxito", f"Supervisor {nombre} agregado correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar: {e}")


class EditarSupervisorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("✏️ Editar Supervisor")
        self.resize(520, 520)
        self.setWindowIcon(QIcon("assets/logos/transparente.png"))

        self.setStyleSheet("""
            QDialog { background-color: #3f3f3f; color: #E0E1DD; font-family: 'Segoe UI'; }
            QLabel { background: transparent; color: #E0E1DD; font-size: 13px; font-weight: 600; margin-top: 6px; }
            QLineEdit {
                background: #8b8b8b;
                border: 1px solid #3f3f3f;
                border-radius: 8px;
                color: #E0E1DD;
                padding: 8px 10px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #E0E1DD;
                background: #8b8b8b;
            }
            QPushButton {
                background-color: #8b8b8b;
                border: none;
                color: #E0E1DD;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #a0a0a0; }
            QPushButton:pressed { background-color: #707070; }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Editar Información de Supervisor")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addWidget(QLabel("Buscar por ID del Supervisor"))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Ej: 102")
        layout.addWidget(self.id_input)

        self.buscar_btn = QPushButton("🔎 Buscar Supervisor")
        self.buscar_btn.clicked.connect(self.buscar_supervisor)
        layout.addWidget(self.buscar_btn)

        layout.addWidget(QLabel("RUT"))
        self.rut_input = QLineEdit()
        layout.addWidget(self.rut_input)

        layout.addWidget(QLabel("Dígito Verificador"))
        self.dv_input = QLineEdit()
        layout.addWidget(self.dv_input)

        layout.addWidget(QLabel("Nombre"))
        self.nombre_input = QLineEdit()
        layout.addWidget(self.nombre_input)

        layout.addWidget(QLabel("Apellido"))
        self.apellido_input = QLineEdit()
        layout.addWidget(self.apellido_input)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancelar_btn)

        self.guardar_btn = QPushButton("💾 Guardar Cambios")
        self.guardar_btn.clicked.connect(self.guardar_cambios)
        btn_layout.addWidget(self.guardar_btn)

        layout.addItem(QSpacerItem(10, 15, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def buscar_supervisor(self):
        id_supervisor = self.id_input.text().strip()
        if not id_supervisor:
            QMessageBox.warning(self, "Error", "Debe ingresar un ID válido.")
            return

        try:
            datos = obtener_supervisor_por_id(id_supervisor)
            if datos:
                self.rut_input.setText(str(datos["Rut_Supervisor"]))
                self.dv_input.setText(str(datos["Digito_Verificador"]))
                self.nombre_input.setText(str(datos["Nombre_Supervisor"]))
                self.apellido_input.setText(str(datos["Apellido_Supervisor"]))
            else:
                QMessageBox.warning(self, "Sin resultados", "No se encontró ningún supervisor con ese ID.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo buscar: {e}")

    def guardar_cambios(self):
        id_supervisor = self.id_input.text().strip()
        rut = self.rut_input.text().strip()
        digito = self.dv_input.text().strip()
        nombre = self.nombre_input.text().strip()
        apellido = self.apellido_input.text().strip()

        if not id_supervisor or not rut or not digito or not nombre or not apellido:
            QMessageBox.warning(self, "Error", "Debe completar todos los campos antes de guardar.")
            return

        try:
            actualizar_supervisor(id_supervisor, rut, digito, nombre, apellido)
            QMessageBox.information(self, "Éxito", "Datos actualizados correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar: {e}")


class EliminarSupervisorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🗑️ Eliminar Supervisor")
        self.resize(420, 280)
        self.setWindowIcon(QIcon("assets/logos/transparente.png"))

        self.setStyleSheet("""
            QDialog { background-color: #3f3f3f; color: #E0E1DD; font-family: 'Segoe UI'; }
            QLabel { background: transparent; font-size: 13px; font-weight: 600; color: #8b8b8b; margin-top: 6px; }
            QLineEdit { background: transparent; color: #E0E1DD; border: 1px solid #8b8b8b; border-radius: 8px; padding: 8px 10px; font-size: 13px; }
            QLineEdit:focus { border: 1px solid #E0E1DD; background: transparent; }
            QPushButton { background-color: #8b8b8b; border: none; color: #3f3f3f; font-weight: bold; border-radius: 10px; padding: 10px 16px; font-size: 14px; }
            QPushButton:hover { background-color: #E0E1DD; color: #3f3f3f; }
            QPushButton:pressed { background-color: #3f3f3f; color: #E0E1DD; border: 1px solid #E0E1DD; }
            QLabel#info_label { font-size: 13px; color: #E0E1DD; margin-top: 8px; }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Eliminar Información de Supervisor")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addWidget(QLabel("Buscar por ID del Supervisor"))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Ej: 205")
        layout.addWidget(self.id_input)

        self.buscar_btn = QPushButton("🔎 Buscar Supervisor")
        self.buscar_btn.clicked.connect(self.buscar_supervisor)
        layout.addWidget(self.buscar_btn)

        self.info_label = QLabel("")
        self.info_label.setObjectName("info_label")
        self.info_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.info_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancelar_btn)

        self.eliminar_btn = QPushButton("🗑️ Eliminar Supervisor")
        self.eliminar_btn.clicked.connect(self.eliminar_supervisor)
        self.eliminar_btn.setEnabled(False)
        btn_layout.addWidget(self.eliminar_btn)

        layout.addItem(QSpacerItem(10, 15, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def buscar_supervisor(self):
        id_supervisor = self.id_input.text().strip()
        if not id_supervisor:
            QMessageBox.warning(self, "Error", "Debe ingresar un ID válido.")
            return

        try:
            datos = obtener_supervisor_por_id(id_supervisor)
            if datos:
                self.info_label.setText(
                    f"Nombre: {datos['Nombre_Supervisor']} {datos['Apellido_Supervisor']}\n"
                    f"RUT: {datos['Rut_Supervisor']}-{datos['Digito_Verificador']}"
                )
                self.eliminar_btn.setEnabled(True)
            else:
                QMessageBox.warning(self, "Sin resultados", "No se encontró ningún supervisor con ese ID.")
                self.info_label.setText("")
                self.eliminar_btn.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo buscar: {e}")

    def eliminar_supervisor(self):
        id_supervisor = self.id_input.text().strip()
        if not id_supervisor:
            return

        confirmar = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Estás seguro de eliminar el supervisor con ID {id_supervisor}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmar == QMessageBox.No:
            return

        try:
            eliminar_supervisor(id_supervisor)
            QMessageBox.information(self, "Éxito", "Supervisor eliminado correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")


#-------------------------------- LOGIN-------------------------------------------------

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(650, 500)

        self.tipo_usuario = None
        self.id_usuario = None
        self.offset = None  # Para mover la ventana

        # --- Contenedor principal ---
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(40, 40, 40, 40)  # 🔹 Márgenes visibles alrededor
        main_layout.setSpacing(0)


        # ===============================
        # 🔷 BARRA DE TÍTULO PERSONALIZADA
        # ===============================
        title_bar = QFrame()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("""
            QFrame {
                background-color: #232323;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
        """)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.setSpacing(8)

        # 🧭 Ruta base del proyecto
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # --- Logo pequeño (barra) ---
        logo_bar_path = os.path.join(base_dir, "..", "assets", "logos", "logochico.png")
        logo_bar_path = os.path.normpath(logo_bar_path)

        logo_icon = QLabel()
        if os.path.exists(logo_bar_path):
            pixmap_icon = QPixmap(logo_bar_path).scaled(22, 22, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_icon.setPixmap(pixmap_icon)
        else:
            logo_icon.setText("📄")
            logo_icon.setStyleSheet("color: white; font-size: 16px;")
        title_layout.addWidget(logo_icon)

        # Texto de título
        title_label = QLabel("CallFlash - Iniciar Sesión")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        # Botón cerrar
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #aaa;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                color: #ff5c5c;
            }
        """)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)

        main_layout.addWidget(title_bar)

        # ===============================
        # 🔶 CUERPO PRINCIPAL (LOGIN CARD)
        # ===============================
        card_container = QFrame()
        card_container.setStyleSheet("""
            QFrame {
                background-color: #646464;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
                color: white;
            }
        """)
        card_layout = QVBoxLayout(card_container)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setContentsMargins(0, 30, 0, 20)

        # --- Tarjeta ---
        card = QFrame()
        card.setMaximumWidth(500)   # 🔹 Evita que toque los bordes laterales
        card.setMaximumHeight(550)  # 🔹 Opcional

        card.setStyleSheet("""
            QFrame {
                background-color: #404040;
                border-radius: 12px;
            }
        """)
        inner_layout = QVBoxLayout(card)
        inner_layout.setContentsMargins(30, 30, 30, 30)
        inner_layout.setSpacing(15)
        inner_layout.setAlignment(Qt.AlignCenter)

        # --- Efecto sombra ---
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 160))
        card.setGraphicsEffect(shadow)

        # --- Logo principal ---
        logo_main_path = os.path.join(base_dir, "..", "assets", "logos", "logo.png")
        logo_main_path = os.path.normpath(logo_main_path)

        logo = QLabel()
        logo.setAlignment(Qt.AlignCenter)
        if os.path.exists(logo_main_path):
            pixmap = QPixmap(logo_main_path).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pixmap)
        else:
            logo.setText("🖼️ Logo principal no encontrado")
            logo.setStyleSheet("color: #ff6b6b; font-size: 13px;")
        inner_layout.addWidget(logo)

        # --- Campos ---
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario")
        self.user_input.setStyleSheet("""
            QLineEdit {
                background-color: #898989;
                border: 1px solid #000000;
                border-radius: 8px;
                padding: 8px 10px;
                color: black;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #000000;
                background-color: #FFFDFD;
            }
        """)
        inner_layout.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setStyleSheet("""
            QLineEdit {
                background-color: #898989;
                border: 1px solid #000000;
                border-radius: 8px;
                padding: 8px 10px;
                color: black;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #000000;
                background-color: #FFFDFD;
            }
        """)
        inner_layout.addWidget(self.pass_input)

        # --- Botón Ingresar ---
        self.login_btn = QPushButton("Iniciar sesión")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border-radius: 8px;
                color: black;
                padding: 10px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #7B7B7B;
            }
            QPushButton:pressed {
                background-color: #7B7B7B;
            }
        """)
        inner_layout.addWidget(self.login_btn)

        footer = QLabel("© CallFlash")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #888; font-size: 11px; margin-top: 10px;")
        inner_layout.addWidget(footer)

        card_layout.addWidget(card)
        main_layout.addWidget(card_container)

        self.login_btn.clicked.connect(self.try_login)

    # ===============================
    # 🖱️ Movimiento de ventana
    # ===============================
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if self.offset and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.offset = None

    # ===============================
    # 🔐 Lógica de autenticación
    # ===============================
    def try_login(self):
        usuario = self.user_input.text().strip()
        clave = self.pass_input.text().strip()

        # ⚠️ Validar campos vacíos
        if not usuario or not clave:
            msg = QMessageBox(self)
            msg.setWindowTitle("Campos vacíos")
            msg.setText("Por favor completa ambos campos.")
            msg.setIcon(QMessageBox.Warning)

            # 🔹 Estilos personalizados (modo oscuro)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1e1e2f;
                    color: #f8f8f8;
                    border-radius: 10px;
                    font-size: 14px;
                    font-family: 'Segoe UI';
                }
                QPushButton {
                    background-color: #7C5DFA;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #937BFF;
                }
            """)
            msg.exec_()
            return

        # ✅ Verificar credenciales
        datos = check_user_credentials(usuario, clave)
        if datos:
            self.id_usuario = datos["usuario"]
            self.tipo_usuario = datos["tipo_usuario"]
            print("✅ Usuario autenticado:", datos)
            self.accept()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("Usuario o contraseña incorrectos.")
            msg.setIcon(QMessageBox.Critical)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1e1e2f;
                    color: #f8f8f8;
                    border-radius: 10px;
                    font-size: 14px;
                    font-family: 'Segoe UI';
                }
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            msg.exec_()


    

