import sqlite3

DB = "inventario.db"

def conectar():
    return sqlite3.connect(DB)

def crear_tablas():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        password TEXT,
        rol TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        nombre TEXT,
        descripcion TEXT,
        categoria TEXT,
        cantidad INTEGER,
        unidad TEXT,
        costo REAL,
        precio REAL,
        estado TEXT,
        stock_minimo INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS movimientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        tipo TEXT,
        producto_id INTEGER,
        cantidad INTEGER,
        usuario TEXT,
        motivo TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        total REAL,
        usuario TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS detalle_ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER,
        producto TEXT,
        cantidad INTEGER,
        precio REAL,
        subtotal REAL
    )
    """)

    conn.commit()
    conn.close()

