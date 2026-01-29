import datetime
import getpass
import database

# ===============================
# INICIALIZAR BASE DE DATOS
# ===============================
database.crear_tablas()

def ejecutar(sql, parametros=(), fetch=False):
    conn = database.conectar()
    cursor = conn.cursor()
    cursor.execute(sql, parametros)
    data = cursor.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

# ===============================
# LOGIN
# ===============================
def login():
    usuario = input("Usuario: ")
    password = getpass.getpass("Contraseña: ")

    data = ejecutar(
        "SELECT rol FROM usuarios WHERE usuario=? AND password=?",
        (usuario, password),
        True
    )

    if data:
        return usuario, data[0][0]
    else:
        print(" Credenciales incorrectas")
        return None, None

# ===============================
# USUARIOS
# ===============================
def crear_usuario():
    usuario = input("Usuario: ")
    password = getpass.getpass("Contraseña: ")
    rol = input("Rol (admin/caja): ")

    try:
        ejecutar(
            "INSERT INTO usuarios VALUES (NULL,?,?,?)",
            (usuario, password, rol)
        )
        print(" Usuario creado")
    except:
        print(" Usuario ya existe")

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

    ejecutar("""
    INSERT INTO productos 
    VALUES (NULL,?,?,?,?,?,?,?,?,?,?)
    """, datos)

    print(" Producto registrado")

def ver_inventario():
    productos = ejecutar("""
    SELECT codigo, nombre, cantidad, unidad, precio 
    FROM productos
    """, fetch=True)

    print("\n INVENTARIO")
    for p in productos:
        print(p)

# ===============================
# MOVIMIENTOS
# ===============================
def entrada(usuario):
    codigo = input("Código: ")
    cantidad = int(input("Cantidad entrada: "))
    motivo = input("Motivo: ")

    prod = ejecutar(
        "SELECT id FROM productos WHERE codigo=?",
        (codigo,), True
    )

    if prod:
        pid = prod[0][0]
        ejecutar("UPDATE productos SET cantidad = cantidad + ? WHERE id=?", (cantidad, pid))
        ejecutar(
            "INSERT INTO movimientos VALUES (NULL,?,?,?,?,?)",
            (str(datetime.date.today()), "entrada", pid, cantidad, usuario, motivo)
        )
        print(" Entrada registrada")
    else:
        print(" Producto no encontrado")

def salida(usuario):
    codigo = input("Código: ")
    cantidad = int(input("Cantidad salida: "))
    motivo = input("Motivo: ")

    prod = ejecutar(
        "SELECT id, cantidad FROM productos WHERE codigo=?",
        (codigo,), True
    )

    if prod and prod[0][1] >= cantidad:
        pid = prod[0][0]
        ejecutar("UPDATE productos SET cantidad = cantidad - ? WHERE id=?", (cantidad, pid))
        ejecutar(
            "INSERT INTO movimientos VALUES (NULL,?,?,?,?,?)",
            (str(datetime.date.today()), "salida", pid, cantidad, usuario, motivo)
        )
        print(" Venta registrada")
    else:
        print(" Stock insuficiente")

# ===============================
# REPORTES
# ===============================
def stock_bajo():
    datos = ejecutar("""
    SELECT nombre, cantidad, stock_minimo 
    FROM productos 
    WHERE cantidad <= stock_minimo
    """, fetch=True)

    print("\n STOCK BAJO")
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
3. Entrada
4. Crear usuario
5. Stock bajo
0. Salir
""")
        op = input("Opción: ")

        if op == "1": registrar_producto()
        elif op == "2": ver_inventario()
        elif op == "3": entrada(usuario)
        elif op == "4": crear_usuario()
        elif op == "5": stock_bajo()
        elif op == "0": break

def menu_caja(usuario):
    while True:
        print("""
1. Ver inventario
2. Venta
0. Salir
""")
        op = input("Opción: ")

        if op == "1": ver_inventario()
        elif op == "2": salida(usuario)
        elif op == "0": break

# ===============================
# EJECUCIÓN
# ===============================
print("SISTEMA DE INVENTARIO\n")

usuario, rol = login()

if rol == "admin":
    menu_admin(usuario)
elif rol == "caja":
    menu_caja(usuario)
