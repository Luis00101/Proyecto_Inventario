import datetime
import hashlib
import database

database.crear_tablas()

# ===============================
def ejecutar(sql, parametros=(), fetch=False):
    conn = database.conectar()
    c = conn.cursor()
    c.execute(sql, parametros)
    data = c.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ===============================
# ADMIN AUTOMÁTICO
# ===============================
def crear_admin():
    admin_pass = hash_pass("admin123")
    try:
        ejecutar(
            "INSERT INTO usuarios VALUES (NULL,?,?,?)",
            ("admin", admin_pass, "admin")
        )
        print("Admin creado (admin / admin123)")
    except:
        pass

crear_admin()

# ===============================
# LOGIN
# ===============================
def login():
    usuario = input("Usuario: ")
    password = hash_pass(input("Contraseña: "))

    data = ejecutar(
        "SELECT rol FROM usuarios WHERE usuario=? AND password=?",
        (usuario, password), True
    )

    if data:
        return usuario, data[0][0]

    print("Credenciales incorrectas")
    return None, None

# ===============================
# CREAR USUARIOS
# ===============================
def crear_usuario():
    print("\nCREAR USUARIO")
    usuario = input("Usuario: ")
    password = hash_pass(input("Contraseña: "))
    rol = input("Rol (admin/caja): ").lower()

    if rol not in ("admin", "caja"):
        print("Rol inválido")
        return

    try:
        ejecutar(
            "INSERT INTO usuarios VALUES (NULL,?,?,?)",
            (usuario, password, rol)
        )
        print("Usuario creado correctamente")
    except:
        print("El usuario ya existe")

# ===============================
# PRODUCTOS
# ===============================
def registrar_producto():
    datos = (
        input("Código: "),
        input("Nombre: "),
        input("Descripción: "),
        input("Categoría: "),
        int(input("Cantidad: ")),
        input("Unidad: "),
        float(input("Costo: ")),
        float(input("Precio: ")),
        "activo",
        int(input("Stock mínimo: "))
    )
    ejecutar("INSERT INTO productos VALUES (NULL,?,?,?,?,?,?,?,?,?,?)", datos)
    print("Producto registrado")

def ver_inventario():
    productos = ejecutar("""
    SELECT codigo,nombre,cantidad,unidad,precio
    FROM productos WHERE estado='activo'
    """, True)

    print("\nINVENTARIO")
    for p in productos:
        print(f"{p[0]} | {p[1]} | {p[2]} {p[3]} | ${p[4]}")

# ===============================
# VENTAS + TICKET
# ===============================
def venta(usuario):
    carrito = []
    total = 0

    while True:
        codigo = input("Código producto (0 terminar): ")
        if codigo == "0":
            break

        prod = ejecutar(
            "SELECT id,nombre,precio,cantidad FROM productos WHERE codigo=?",
            (codigo,), True
        )

        if not prod:
            print("No existe")
            continue

        cantidad = int(input("Cantidad: "))
        if cantidad > prod[0][3]:
            print("Stock insuficiente")
            continue

        subtotal = cantidad * prod[0][2]
        carrito.append((prod[0][0], prod[0][1], cantidad, prod[0][2], subtotal))
        total += subtotal

    if not carrito:
        return

    ejecutar(
        "INSERT INTO ventas VALUES (NULL,?,?,?)",
        (str(datetime.date.today()), total, usuario)
    )

    venta_id = ejecutar("SELECT MAX(id) FROM ventas", fetch=True)[0][0]

    print("\nTICKET")
    for c in carrito:
        ejecutar(
            "UPDATE productos SET cantidad=cantidad-? WHERE id=?",
            (c[2], c[0])
        )
        ejecutar(
            "INSERT INTO detalle_ventas VALUES (NULL,?,?,?,?,?)",
            (venta_id, c[1], c[2], c[3], c[4])
        )
        ejecutar(
            "INSERT INTO movimientos VALUES (NULL,?,?,?,?,?,?)",
            (str(datetime.date.today()), "salida", c[0], c[2], usuario, "Venta")
        )
        print(f"{c[1]} x{c[2]} = ${c[4]}")

    print(f"TOTAL: ${total}")
    print("Venta realizada\n")

# ===============================
# REPORTES
# ===============================
def ventas_totales():
    datos = ejecutar("SELECT fecha,total,usuario FROM ventas", True)
    print("\nVENTAS")
    for d in datos:
        print(d)

def stock_bajo():
    datos = ejecutar("""
    SELECT nombre,cantidad FROM productos
    WHERE cantidad<=stock_minimo
    """, True)
    print("\nSTOCK BAJO")
    for d in datos:
        print(d)

# ===============================
# MENÚS
# ===============================
def menu_admin(usuario):
    while True:
        print("""
1. Registrar producto
2. Ver inventario
3. Venta
4. Ver ventas
5. Stock bajo
6. Crear usuario
0. Cerrar sesión
""")
        op = input("Opción: ")

        if op == "1": registrar_producto()
        elif op == "2": ver_inventario()
        elif op == "3": venta(usuario)
        elif op == "4": ventas_totales()
        elif op == "5": stock_bajo()
        elif op == "6": crear_usuario()
        elif op == "0": break

def menu_caja(usuario):
    while True:
        print("""
1. Ver inventario
2. Venta
0. Cerrar sesión
""")
        op = input("Opción: ")

        if op == "1": ver_inventario()
        elif op == "2": venta(usuario)
        elif op == "0": break

# ===============================
# EJECUCIÓN
# ===============================
print("SISTEMA DE INVENTARIO")

while True:
    usuario, rol = login()
    if rol == "admin":
        menu_admin(usuario)
    elif rol == "caja":
        menu_caja(usuario)

