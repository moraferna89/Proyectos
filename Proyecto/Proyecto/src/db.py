import pymysql

# ------------------- CONEXIÓN -------------------
def conectar():
    return pymysql.connect(
        host="34.176.144.222",        # IP pública de tu instancia Cloud SQL
        user="proyecto_bd",                  # usuario con permisos remotos
        password= "Hola.1234", # tu contraseña, raw string para caracteres especiales
        database="bdproyecto",        # nombre de la base de datos importada
        cursorclass=pymysql.cursors.DictCursor,
        port=3306
    )

# ------------------- EJECUTIVOS -------------------
def obtener_ejecutivos():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM ejecutivo")
    resultado = cursor.fetchall()
    conexion.close()
    return resultado

def agregar_ejecutivo(rut, dv, nombre, apellido, rol):
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
        INSERT INTO ejecutivo (Rut_Ejecutivo,Digito_Verificador,Nombre_Ejecutivo, Apellido_Ejecutivo, TCARGO_Id_Tipo_Cargo)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (rut, dv, nombre, apellido, rol))
    conexion.commit()
    conexion.close()

def agregar_supervisor(rut, dv, nombre, apellido):
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
        INSERT INTO ejecutivo (Rut_Supervisor,Digito_Verificador,Nombre_Supervisor, Apellido_Supervisor)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (rut, dv, nombre, apellido))
    conexion.commit()
    conexion.close()

def obtener_ejecutivo_por_id(id_ejecutivo):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM ejecutivo WHERE Id_ejecutivo = %s", (id_ejecutivo,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado

def obtener_supervisor_por_id(id_supervisor):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM supervisor WHERE Id_supervisor = %s", (id_supervisor,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado

def actualizar_ejecutivo(id_ejecutivo, rut, digito, nombre, apellido, tipo_cargo):
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
        UPDATE ejecutivo
        SET Rut_Ejecutivo = %s,
            Digito_Verificador = %s,
            Nombre_Ejecutivo = %s,
            Apellido_Ejecutivo = %s,
            TCARGO_Id_Tipo_Cargo = %s
        WHERE Id_ejecutivo = %s
    """
    cursor.execute(query, (rut, digito, nombre, apellido, tipo_cargo, id_ejecutivo))
    conexion.commit()
    conexion.close()

def actualizar_supervisor(id_ejecutivo, rut, digito, nombre, apellido):
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
        UPDATE ejecutivo
        SET Rut_Ejecutivo = %s,
            Digito_Verificador = %s,
            Nombre_Ejecutivo = %s,
            Apellido_Ejecutivo = %s,
        WHERE Id_ejecutivo = %s
    """
    cursor.execute(query, (rut, digito, nombre, apellido,  id_ejecutivo))
    conexion.commit()
    conexion.close()


def eliminar_ejecutivo(id_ejecutivo):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM ejecutivo WHERE Id_ejecutivo = %s", (id_ejecutivo,))
    conexion.commit()
    conexion.close()

def eliminar_supervisor(id_supervisor):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM supervisor WHERE Id_supervisor = %s", (id_supervisor,))
    conexion.commit()
    conexion.close()


# ------------------- LLAMADAS -------------------
def obtener_llamadas():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM llamada")
    resultado = cursor.fetchall()
    conexion.close()
    return resultado

def obtener_llamada_por_id(id_llamada):
    conexion = conectar()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT 
            l.*, 
            c.Clasificacion AS Nombre_Clasificacion
        FROM llamada l 
        JOIN clasifi_llam c 
            ON l.CLASIFI_LLAMADA_Id_Clasifi_Llam = c.id_clasifi_llam
        WHERE l.Id_llamadas = %s
    """, (id_llamada,))
    
    resultado = cursor.fetchone()
    conexion.close()
    return resultado



def actualizar_audio_llamada(id_llamada, contenido_audio):
    """
    Guarda el audio (BLOB) en la llamada correspondiente
    """
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE llamada SET audio_llamada=%s WHERE Id_llamadas=%s",
        (contenido_audio, id_llamada)
    )
    conexion.commit()
    conexion.close()

def agregar_llamada(fecha,hora,id_ejecutivo, id_cliente, id_supervisor, id_clasificacion,  audio_path):
    conn = conectar()
    cursor = conn.cursor()

    # Leer el archivo de audio como binario (BLOB)
    with open(audio_path, "rb") as f:
        audio_data = f.read()

    # ⚠️ No se incluye Id_llamada (MySQL lo autogenera)
    query = """
        INSERT INTO llamada
        (Fecha,Hora, EJECUTIVO_Id_ejecutivo, CLIENTE_Id_cliente, SUPERVISOR_Id_Supervisor, 
         CLASIFI_LLAMADA_Id_Clasifi_Llam, audio_llamada)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (fecha , hora, id_ejecutivo, id_cliente, id_supervisor, id_clasificacion, audio_data))
    conn.commit()

    # Si quieres obtener el ID generado automáticamente:
    nuevo_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return nuevo_id  # opcional

def eliminar_llamada(id_llamada):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM llamada WHERE Id_llamadas = %s", (id_llamada,))
    conexion.commit()
    conexion.close()


#<-----------------------CLIENTE-------------------------->
def agregar_cliente(rut, dv, nombre,apellido):
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
        INSERT INTO cliente (Rut_Cliente,Digito_Verificador,Nombre_Cliente, Apellido_Cliente)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (rut, dv, nombre,apellido))
    conexion.commit()
    conexion.close()


def eliminar_cliente(id_cliente):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM cliente WHERE Id_cliente = %s", (id_cliente,))
    conexion.commit()
    conexion.close()

def obtener_cliente_por_id(id_cliente):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM cliente WHERE Id_cliente = %s", (id_cliente,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado

def actualizar_cliente(id_cliente, rut, digito, nombre, apellido):
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
        UPDATE cliente
        SET Rut_Cliente = %s,
            Digito_Verificador = %s,
            Nombre_Cliente = %s,
            Apellido_Cliente = %s
        WHERE id_cliente = %s
    """
    cursor.execute(query, (rut, digito, nombre, apellido,  id_cliente))
    conexion.commit()
    conexion.close()



#<---------------- INICIO DE SESION-------------->
def check_user_credentials(usuario: str, clave: str):
    """
    Consulta la base de datos para verificar usuario y contraseña.
    Retorna un dict con 'usuario' y 'tipo_usuario' si existe, None si no.
    Convierte tipo "SUP" a "admin".
    """
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor(pymysql.cursors.DictCursor)  # cursor que devuelve dict
        query = "SELECT usuario, tipo_cargo FROM usuario WHERE usuario=%s AND clave=%s"
        cursor.execute(query, (usuario, clave))
        result = cursor.fetchone()
        if result:
            tipo_cargo = result["tipo_cargo"]
            if tipo_cargo.upper() == "SUP":
                tipo_cargo = "admin"
            return {"usuario": result["usuario"], "tipo_usuario": tipo_cargo}
        return None
    except pymysql.MySQLError as err:
        print("❌ Error al consultar BD:", err)
        return None
    finally:
        if cursor: cursor.close()
        if conn: conn.close()






def obtener_top3_efectividad():
    """
    Retorna los 3 ejecutivos con mayor promedio de efectividad.
    Cada fila es un diccionario: {"ejecutivo": ..., "total_puntos": ..., "total_llamadas": ..., "promedio_efectividad": ...}
    """
    conn = conectar()
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # importante: devuelve diccionarios

    query = """
        SELECT
            CONCAT(e.Nombre_Ejecutivo, ' ', e.Apellido_Ejecutivo) AS ejecutivo,
            SUM(l.CLASIFI_LLAMADA_Id_Clasifi_Llam) AS total_puntos,
            COUNT(*) AS total_llamadas,
            SUM(l.CLASIFI_LLAMADA_Id_Clasifi_Llam) / COUNT(*) AS promedio_efectividad
        FROM llamada l
        JOIN ejecutivo e ON l.EJECUTIVO_Id_ejecutivo = e.id_ejecutivo
        GROUP BY e.Id_ejecutivo, e.Nombre_Ejecutivo, e.Apellido_Ejecutivo
        ORDER BY promedio_efectividad DESC
        LIMIT 3
    """

    cursor.execute(query)
    resultados = cursor.fetchall()  # lista de diccionarios
    cursor.close()
    conn.close()

    return resultados

def cantidad_llamadas():
    conexion = conectar()
    cursor = conexion.cursor()  # si quieres DictCursor explícito: cursor = conexion.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT COUNT(id_llamadas) AS total FROM llamada")
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    return resultado["total"] if resultado else 0

# db.py
def obtener_datos_usuario(id_usuario):
    print("🔹 obtener_datos_usuario llamado con id_usuario:", id_usuario)
    conn = conectar()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 1️⃣ Primero detectamos el tipo de cargo del usuario
    tipo_query = """
    SELECT u.tipo_Cargo AS cargo
    FROM usuario u
    JOIN ejecutivo e ON u.usuario = e.Rut_Ejecutivo
    JOIN tcargo t ON e.TCARGO_Id_Tipo_Cargo = t.Id_Tipo_Cargo
    where u.usuario= %s
    """
    cursor.execute(tipo_query, (id_usuario,))
    tipo_resultado = cursor.fetchone()

    if tipo_resultado:
        cargo = tipo_resultado["cargo"].strip().upper()
        print(f"🔍 Tipo de cargo detectado: {cargo}")
    else:
        # Si no se encuentra en ejecutivo, probamos si es supervisor
        cargo = None
        print("⚠️ No se encontró tipo de cargo en tabla ejecutivo, probando supervisor...")

    resultado = None

    # 2️⃣ Si es EJECUTIVO
    if cargo == "EJE" or cargo == "EJECUTIVO":
        query = """
        SELECT
            e.Rut_Ejecutivo AS rut,
            e.nombre_ejecutivo AS nombre,
            e.Apellido_Ejecutivo AS apellido,
            t.Tipo_Cargo AS cargo
        FROM usuario u
        JOIN ejecutivo e ON u.usuario = e.Rut_Ejecutivo
        JOIN tcargo t ON e.TCARGO_Id_Tipo_Cargo = t.Id_Tipo_Cargo
        WHERE u.usuario = %s
        """
        cursor.execute(query, (id_usuario,))
        resultado = cursor.fetchone()

    # 3️⃣ Si es SUPERVISOR / ADMIN
    elif cargo == "SUP" or cargo == "SUPERVISOR" or cargo == "ADMIN":
        query = """
        SELECT
            u.usuario,
            s.Rut_Supervisor AS rut,
            s.Nombre_Supervisor AS nombre,
            s.Apellido_Supervisor AS apellido,
            'Supervisor' AS cargo
        FROM usuario u
        JOIN supervisor s ON u.usuario = s.Rut_Supervisor
        WHERE u.usuario = %s
        """
        cursor.execute(query, (id_usuario,))
        resultado = cursor.fetchone()

    else:
        # Si no se detectó cargo, probamos si es supervisor directamente
        print("⚠️ No se detectó cargo en ejecutivo, verificando si pertenece a supervisor...")
        query = """
        SELECT
            u.usuario,
            s.Rut_Supervisor AS rut,
            s.Nombre_Supervisor AS nombre,
            s.Apellido_Supervisor AS apellido,
            'Supervisor' AS cargo
        FROM usuario u
        JOIN supervisor s ON u.usuario = s.Rut_Supervisor
        WHERE u.usuario = %s
        """
        cursor.execute(query, (id_usuario,))
        resultado = cursor.fetchone()

    print("🔹 Resultado de la consulta:", resultado)

    cursor.close()
    conn.close()

    if resultado:
        print("✅ Datos encontrados:", resultado)
    else:
        print("⚠️ No se encontraron datos para este usuario")

    return resultado or {}




def obtener_llamadas_xejecutivo(id_usuario):
    conexion = conectar()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    query = """
        SELECT 
            l.id_llamadas,
            l.Fecha,
            l.Hora,
            l.EJECUTIVO_Id_ejecutivo,
            l.CLIENTE_Id_cliente,
            l.SUPERVISOR_Id_supervisor,
            l.CLASIFI_LLAMADA_Id_Clasifi_Llam,
            e.id_ejecutivo,
            e.Rut_Ejecutivo,
            e.Digito_Verificador,
            e.Nombre_Ejecutivo,
            e.Apellido_Ejecutivo,
            e.TCARGO_Id_Tipo_Cargo
        FROM llamada l
        JOIN ejecutivo e ON l.EJECUTIVO_Id_ejecutivo = e.id_ejecutivo
        WHERE e.Rut_Ejecutivo = %s
        LIMIT 4
    """

    cursor.execute(query, (id_usuario,))
    resultados = cursor.fetchall()

    cursor.close()
    conexion.close()

    return resultados or []


def obtener_todasllamadas_xejecutivo(id_usuario):
    conexion = conectar()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    query = """
        SELECT 
            l.id_llamadas,
            l.Fecha,
            l.Hora,
            l.EJECUTIVO_Id_ejecutivo,
            l.CLIENTE_Id_cliente,
            l.SUPERVISOR_Id_supervisor,
            l.CLASIFI_LLAMADA_Id_Clasifi_Llam,
            e.id_ejecutivo,
            e.Rut_Ejecutivo,
            e.Digito_Verificador,
            e.Nombre_Ejecutivo,
            e.Apellido_Ejecutivo,
            e.TCARGO_Id_Tipo_Cargo
        FROM llamada l
        JOIN ejecutivo e ON l.EJECUTIVO_Id_ejecutivo = e.id_ejecutivo
        WHERE e.Rut_Ejecutivo = %s
    """

    cursor.execute(query, (id_usuario,))
    resultados = cursor.fetchall()

    cursor.close()
    conexion.close()

    return resultados or []





#<---------------------MENSAJES--------------------->


# 🟢 Guardar un nuevo mensaje
def guardar_mensaje(remitente_id, destinatario_id, mensaje):
    print("💬 Guardando mensaje:", remitente_id, "→", destinatario_id, mensaje)
    conexion = conectar()
    cursor = conexion.cursor()
    sql = "INSERT INTO mensajes (remitente_id, destinatario_id, mensaje) VALUES (%s, %s, %s)"
    cursor.execute(sql, (remitente_id, destinatario_id, mensaje))
    conexion.commit()
    cursor.close()
    conexion.close()



# 🟢 Obtener conversación entre dos usuarios
def obtener_conversacion(usuario_a, usuario_b, limit=100, asc=True):
    conexion = conectar()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    orden = "ASC" if asc else "DESC"

    sql = f"""
        SELECT 
            m.id_mensaje,
            m.remitente_id,
            m.destinatario_id,
            m.mensaje,
            m.leido,
            m.fecha_envio,
            u1.usuario AS remitente_nombre,
            u2.usuario AS destinatario_nombre
        FROM mensajes m
        JOIN usuario u1 ON m.remitente_id = u1.usuario
        JOIN usuario u2 ON m.destinatario_id = u2.usuario
        WHERE (m.remitente_id = %s AND m.destinatario_id = %s)
           OR (m.remitente_id = %s AND m.destinatario_id = %s)
        ORDER BY m.fecha_envio {orden}
        LIMIT %s
    """

    cursor.execute(sql, (usuario_a, usuario_b, usuario_b, usuario_a, limit))
    rows = cursor.fetchall()

    cursor.close()
    conexion.close()
    return rows or []


def contar_mensajes_no_leidos(usuario_id):
    conexion = conectar()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT COUNT(*) AS total FROM mensajes WHERE destinatario_id = %s AND leido = 0"
    cursor.execute(sql, (usuario_id,))
    row = cursor.fetchone()
    cursor.close()
    conexion.close()

    return int(row["total"]) if row else 0



# 🟢 Marcar mensajes como leídos
def marcar_como_leido(usuario_destino_id, otro_usuario_id=None):
    conexion = conectar()
    cursor = conexion.cursor()

    if otro_usuario_id:
        sql = """
            UPDATE mensajes
            SET leido = 1
            WHERE destinatario_id = %s AND remitente_id = %s AND leido = 0
        """
        cursor.execute(sql, (usuario_destino_id, otro_usuario_id))
    else:
        sql = """
            UPDATE mensajes
            SET leido = 1
            WHERE destinatario_id = %s AND leido = 0
        """
        cursor.execute(sql, (usuario_destino_id,))

    conexion.commit()
    cursor.close()
    conexion.close()


def obtener_usuarios(excepto_id=None):
    conexion = conectar()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    sql_base = """
        SELECT 
            u.id_usuario,
            u.usuario as usuario,
            COALESCE(
                CONCAT(e.nombre_ejecutivo, ' ', e.apellido_ejecutivo),
                CONCAT(s.nombre_supervisor, ' ', s.apellido_supervisor)
            ) AS nombre,
            CASE 
                WHEN e.id_ejecutivo IS NOT NULL THEN 'ejecutivo'
                WHEN s.id_supervisor IS NOT NULL THEN 'supervisor'
            END AS tipo
        FROM usuario u
        LEFT JOIN ejecutivo e ON u.usuario = e.rut_ejecutivo
        LEFT JOIN supervisor s ON u.usuario = s.rut_supervisor
    """

    if excepto_id:
        sql = sql_base + " WHERE u.id_usuario != %s"
        cursor.execute(sql, (excepto_id,))
    else:
        cursor.execute(sql_base)

    rows = cursor.fetchall()
    cursor.close()
    conexion.close()
    return rows or []

def obtener_mensajes_no_leidos(usuario_id):
    conexion = conectar()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    sql = """
        SELECT COUNT(*) AS total
        FROM mensajes
        WHERE destinatario_id = %s AND leido = 0
    """
    cursor.execute(sql, (usuario_id,))
    resultado = cursor.fetchone()

    cursor.close()
    conexion.close()

    return int(resultado["total"]) if resultado and resultado["total"] is not None else 0

def obtener_usuarios_con_mensajes_no_leidos(usuario_id):
    conexion = conectar()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    sql = """
        SELECT remitente_id
        FROM mensajes
        WHERE destinatario_id = %s AND leido = 0
        GROUP BY remitente_id
    """
    cursor.execute(sql, (usuario_id,))
    resultados = cursor.fetchall()

    cursor.close()
    conexion.close()

    ids = [int(r["remitente_id"]) for r in resultados] if resultados else []
    print("🔔 Usuarios con mensajes no leídos:", ids)  # 👈 Agrega este print temporal
    return ids


def cantidad_llamadasxid(usuario_id):
    conexion = conectar()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    sql = """
        select count(*) as total
        from llamada l join ejecutivo e 
            on(l.EJECUTIVO_Id_ejecutivo=e.id_ejecutivo) 
        where e.rut_ejecutivo= %s
    """
    cursor.execute(sql, (usuario_id,))
    resultado = cursor.fetchone()
    print(resultado)
    cursor.close()
    conexion.close()
    return resultado["total"] if resultado else 0


def promedio_llamadas(usuario_id):
    conexion = conectar()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    sql = """
        select round(sum(CLASIFI_LLAMADA_Id_Clasifi_Llam)/count(*)) as total
        from llamada l join ejecutivo e 
            on(l.EJECUTIVO_Id_ejecutivo=e.id_ejecutivo) 
        where e.rut_ejecutivo= %s
    """
    cursor.execute(sql, (usuario_id,))
    resultado = cursor.fetchone()
    print(resultado)
    cursor.close()
    conexion.close()
    return resultado["total"] if resultado else 0


def obtener_llamadas_reporte():
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
        SELECT id_llamadas as Id,
            Fecha,
            Hora,
            EJECUTIVO_Id_ejecutivo AS 'Id Ejecutivo',
            CLIENTE_Id_cliente as 'Id Cliente',
            SUPERVISOR_Id_supervisor as 'Id Supervisor',
            CLASIFI_LLAMADA_Id_Clasifi_Llam as 'Puntaje Llamada'
        FROM llamada
    """
    cursor.execute(query)
    resultado = cursor.fetchall()
    conexion.close()
    return resultado

def obtener_clientes_reporte():
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
        SELECT id_cliente as Id,
            Rut_Cliente as 'Rut',
            Digito_Verificador as 'Digito Verificador',
            Nombre_Cliente as 'Nombre',
            Apellido_Cliente as Apellido
        FROM cliente
    """
    cursor.execute(query)
    resultado = cursor.fetchall()
    conexion.close()
    return resultado

def obtener_ejecutivos_reporte():
    conexion = conectar()
    cursor = conexion.cursor()
    query = """
        SELECT id_ejecutivo as Id,
            Rut_Ejecutivo as 'Rut',
            Digito_Verificador as 'Digito Verificador',
            Nombre_Ejecutivo as 'Nombre',
            Apellido_Ejecutivo as Apellido,
            TCARGO_Id_Tipo_Cargo as 'Cargo'
        FROM ejecutivo
    """
    cursor.execute(query)
    resultado = cursor.fetchall()
    conexion.close()
    return resultado