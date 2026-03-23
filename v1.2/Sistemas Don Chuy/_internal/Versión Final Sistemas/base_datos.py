import datetime
import hashlib
import sqlite3

def conectar():
    return sqlite3.connect("sistema.db")

def ejecutar(sql, parametros=(), fetch=False):
    conn = conectar()
    c = conn.cursor()
    c.execute(sql, parametros)
    data = c.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

# ================= TABLAS =================
def crear_tablas():
    ejecutar("""CREATE TABLE IF NOT EXISTS usuarios
        (id INTEGER PRIMARY KEY, usuario TEXT UNIQUE, password TEXT, rol TEXT)""")

    ejecutar("""CREATE TABLE IF NOT EXISTS productos
        (id INTEGER PRIMARY KEY, codigo TEXT UNIQUE, nombre TEXT, descripcion TEXT,
        categoria TEXT, cantidad INTEGER, unidad TEXT, costo REAL,
        precio REAL, estado TEXT, stock_minimo INTEGER)""")

    ejecutar("""CREATE TABLE IF NOT EXISTS ventas
        (id INTEGER PRIMARY KEY, fecha TEXT, total REAL, usuario TEXT)""")

    ejecutar("""CREATE TABLE IF NOT EXISTS detalle_ventas
        (id INTEGER PRIMARY KEY, venta_id INTEGER, nombre TEXT,
        cantidad INTEGER, precio REAL, subtotal REAL)""")

crear_tablas()

# ================= LOGIN =================
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def crear_admin():
    try:
        ejecutar("INSERT INTO usuarios VALUES(NULL,?,?,?)",
                ("admin", hash_pass("admin123"), "admin"))
    except:
        pass

crear_admin()

def login(usuario, password):
    data = ejecutar("SELECT rol FROM usuarios WHERE usuario=? AND password=?",
                    (usuario, hash_pass(password)), True)
    return data[0][0] if data else None

# ================= PRODUCTOS =================
def obtener_inventario():
    return ejecutar("SELECT id,codigo,nombre,cantidad,unidad,precio FROM productos WHERE estado='activo'", fetch=True)

def obtener_productos_full():
    return ejecutar("SELECT * FROM productos", fetch=True)

def obtener_producto_por_codigo(codigo):
    return ejecutar("SELECT id,nombre,precio,cantidad FROM productos WHERE codigo=?", (codigo,), True)

def agregar_producto_simple(codigo, nombre, cantidad, precio, stock_min):
    ejecutar("""INSERT INTO productos
        VALUES (NULL,?,?,?,?,?,?,?,?,?,?)""",
        (codigo,nombre,"","General",cantidad,"pz",0,precio,"activo",stock_min))

def actualizar_producto(datos):
    ejecutar("""UPDATE productos SET
        codigo=?, nombre=?, descripcion=?, categoria=?,
        cantidad=?, unidad=?, costo=?, precio=?, estado=?, stock_minimo=?
        WHERE id=?""", datos)

def eliminar_producto(id_producto):
    ejecutar("DELETE FROM productos WHERE id=?", (id_producto,))

# ================= VENTAS =================
def registrar_venta(usuario, carrito, total):
    ejecutar("INSERT INTO ventas VALUES(NULL,?,?,?)",
            (str(datetime.date.today()), total, usuario))
    venta_id = ejecutar("SELECT MAX(id) FROM ventas", fetch=True)[0][0]

    for c in carrito:
        ejecutar("UPDATE productos SET cantidad=cantidad-? WHERE id=?", (c[2], c[0]))
        ejecutar("INSERT INTO detalle_ventas VALUES(NULL,?,?,?,?,?)",
                (venta_id, c[1], c[2], c[3], c[4]))

# ================= REPORTES =================
def ventas_totales():
    return ejecutar("SELECT fecha,total,usuario FROM ventas", fetch=True)

def total_dinero_vendido():
    data = ejecutar("SELECT SUM(total) FROM ventas", fetch=True)
    return data[0][0] if data[0][0] else 0

def total_productos():
    return ejecutar("SELECT COUNT(*) FROM productos", fetch=True)[0][0]

def productos_stock_bajo():
    return ejecutar("SELECT nombre,cantidad FROM productos WHERE cantidad<=stock_minimo", fetch=True)

# ================= USUARIOS =================
def obtener_usuarios():
    return ejecutar("SELECT id,usuario,rol FROM usuarios", fetch=True)

def crear_usuario(usuario,password,rol):
    ejecutar("INSERT INTO usuarios VALUES(NULL,?,?,?)",
            (usuario,hash_pass(password),rol))

def eliminar_usuario(id_usuario):
    ejecutar("DELETE FROM usuarios WHERE id=?", (id_usuario,))
