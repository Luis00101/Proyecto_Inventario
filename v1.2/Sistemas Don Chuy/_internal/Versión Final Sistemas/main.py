import sys
from PyQt5 import QtWidgets
from main_window import Ui_MainWindow
import base_datos as sistema

# =========================
# VENTANA LOGIN
# =========================
class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        
        self.ui.pushButton.clicked.connect(self.login)

        
        self.ui.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)

    def login(self):
        usuario = self.ui.lineEdit_3.text()
        password = self.ui.lineEdit_2.text()

        rol = sistema.login(usuario, password)

        if rol:
            self.abrir_menu(usuario, rol)
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Datos incorrectos")

    def abrir_menu(self, usuario, rol):
        if rol == "admin":
            self.menu = MenuAdmin(usuario, self)
        else:
            self.menu = MenuCaja(usuario, self)

        self.menu.show()
        self.hide()
# ===========================
#   MENU ADMIN
# ==========================
class MenuAdmin(QtWidgets.QWidget):
    def __init__(self, usuario, login_window):
        super().__init__()
        self.usuario = usuario
        self.login_window = login_window
        self.setWindowTitle("MENÚ ADMIN 📋")
        self.showMaximized()

        layout = QtWidgets.QGridLayout()

        btn_dashboard = QtWidgets.QPushButton("Dashboard 🖥️")
        btn_dashboard.clicked.connect(self.abrir_dashboard)

        btn_reportes = QtWidgets.QPushButton("Reportes 🧾")
        btn_reportes.clicked.connect(self.abrir_reportes)

        btn_users = QtWidgets.QPushButton("Administrar usuarios 👤")
        btn_users.clicked.connect(self.abrir_usuarios)

        btn_logout = QtWidgets.QPushButton("Cerrar sesión ⏻")
        btn_logout.clicked.connect(self.cerrar_sesion)

        btn_inv_admin = QtWidgets.QPushButton("Administrar inventario 📋")
        btn_inv_admin.clicked.connect(self.abrir_admin_inventario)
        
        botones = [btn_dashboard, btn_inv_admin,
        btn_reportes, btn_users, btn_logout]

        for b in botones:
            b.setMinimumHeight(80)
            b.setStyleSheet("""
            QPushButton {
            font-size:18px;
            background-color:#4e73df;
            border-radius:15px; }
        QPushButton:hover {
            background-color:#2e59d9;
        }
    """)

        layout.addWidget(btn_dashboard, 0, 0)
        layout.addWidget(btn_inv_admin, 0, 1)
        layout.addWidget(btn_reportes, 1, 0)
        layout.addWidget(btn_users, 1, 1)
        layout.addWidget(btn_logout, 3, 0, 1, 2)

        self.setLayout(layout)

    def abrir_dashboard(self):
        self.win = Dashboard()
        self.win.show()

    def abrir_inventario(self):
        self.win = VentanaInventario()
        self.win.show()

    def abrir_reportes(self):
        self.win = VentanaReportes()
        self.win.show()

    def abrir_usuarios(self):
        self.win = VentanaUsuarios()
        self.win.show()

    def cerrar_sesion(self):
        self.close()
        self.login_window.show()

    def agregar_producto(self):
        
        codigo, ok = QtWidgets.QInputDialog.getText(self,"Código","Código:")
        if not ok or not codigo:
            return

        nombre, ok = QtWidgets.QInputDialog.getText(self,"Nombre","Nombre:")
        if not ok or not nombre:
            return

        cantidad, ok = QtWidgets.QInputDialog.getInt(self,"Cantidad inicial","Cantidad:",1,0)
        if not ok:
            return

        precio, ok = QtWidgets.QInputDialog.getDouble(self,"Precio","Precio:",0,0)
        if not ok:
            return

        stock_min, ok = QtWidgets.QInputDialog.getInt(self,"Stock mínimo","Stock mínimo:",1,0)
        if not ok:
            return

        sistema.agregar_producto_simple(codigo,nombre,cantidad,precio,stock_min)
        QtWidgets.QMessageBox.information(self,"OK","Producto creado correctamente")
        
        self.cargar()
        datos = (codigo, nombre,cantidad, precio,
        "activo", stock_min
    )

    def abrir_admin_inventario(self):
            self.win = VentanaAdminInventario()
            self.win.show()

    def eliminar_producto(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            return

        respuesta = QtWidgets.QMessageBox.question(
            self,"Confirmar","¿Eliminar producto?"
        )

        if respuesta == QtWidgets.QMessageBox.Yes:
            idp = self.tabla.item(fila,0).text()
            sistema.eliminar_producto(idp)
            self.cargar()

# =========================
# MENU CAJA
# =========================
class MenuCaja(QtWidgets.QWidget):
    def __init__(self, usuario, login_window):
        super().__init__()
        self.usuario = usuario
        self.login_window = login_window
        self.setWindowTitle("MENÚ CAJA 🛒")
        self.showMaximized()

        layout = QtWidgets.QGridLayout()

        # ===== BOTONES =====
        btn_venta = QtWidgets.QPushButton("Nueva venta 🛒")
        btn_venta.clicked.connect(self.abrir_venta)

        btn_inv = QtWidgets.QPushButton("Ver inventario 📦")
        btn_inv.clicked.connect(self.abrir_inventario)

        btn_logout = QtWidgets.QPushButton("Cerrar sesión ⏻")
        btn_logout.clicked.connect(self.cerrar_sesion)

        botones = [btn_venta, btn_inv, btn_logout]

        for b in botones:
            b.setMinimumHeight(80)
            b.setStyleSheet("""
                QPushButton {
                    font-size:18px;
                    background-color:#4e73df;
                    color:white;
                    border-radius:15px;
                }
                QPushButton:hover {
                    background-color:#2e59d9;
                }
            """)

        
        layout.addWidget(btn_venta, 0, 0)
        layout.addWidget(btn_inv, 0, 1)
        layout.addWidget(btn_logout, 1, 0, 1, 2)

        self.setLayout(layout)

    def abrir_venta(self):
        self.win = VentanaVenta(self.usuario)
        self.win.show()

    def abrir_inventario(self):
        self.win = VentanaInventario()
        self.win.show()

    def cerrar_sesion(self):
        self.close()
        self.login_window.show()
        
# =========================
# TABLA INVENTARIO
# =========================
class VentanaInventario(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventario")
        self.resize(600,400)

        layout = QtWidgets.QVBoxLayout()
        self.tabla = QtWidgets.QTableWidget()
        layout.addWidget(self.tabla)
        self.setLayout(layout)

        self.cargar_datos()

    def cargar_datos(self):
        datos = sistema.obtener_inventario()

        self.tabla.setRowCount(len(datos))
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
        ["ID","Código","Nombre","Cantidad","Unidad","Precio"]
    )

        for fila, producto in enumerate(datos):
            for col, valor in enumerate(producto):
                self.tabla.setItem(fila, col,
                QtWidgets.QTableWidgetItem(str(valor)))

                
# =========================
# VENTANA REPORTES
# =========================
class VentanaReportes(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reportes")
        self.resize(500,400)

        layout = QtWidgets.QVBoxLayout()

        self.texto = QtWidgets.QTextEdit()
        layout.addWidget(self.texto)

        btn = QtWidgets.QPushButton("Generar reporte")
        btn.clicked.connect(self.generar)
        layout.addWidget(btn)

        self.setLayout(layout)

    def generar(self):
        ventas = sistema.ventas_totales()
        stock_bajo = sistema.productos_stock_bajo()

        reporte = "REPORTE DE VENTAS\n\n"
        for v in ventas:
            reporte += f"{v}\n"

        reporte += "\nPRODUCTOS CON STOCK BAJO\n\n"
        for s in stock_bajo:
            reporte += f"{s}\n"

        self.texto.setText(reporte)

#=====================
# DASHBOARD
#=====================
class Dashboard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard")
        self.resize(400,300)

        layout = QtWidgets.QGridLayout()

        self.lbl_dinero = QtWidgets.QLabel()
        self.lbl_prod = QtWidgets.QLabel()
        self.lbl_stock = QtWidgets.QLabel()

        for lbl in [self.lbl_dinero, self.lbl_prod, self.lbl_stock]:
            lbl.setStyleSheet("""
            background:white;
            padding:20px;
            border-radius:15px;
            font-size:18px;
            font-weight:bold;
            """)

        layout.addWidget(self.lbl_dinero, 0, 0)
        layout.addWidget(self.lbl_prod, 0, 1)
        layout.addWidget(self.lbl_stock, 1, 0)

        btn = QtWidgets.QPushButton("Actualizar")
        btn.clicked.connect(self.cargar)
        layout.addWidget(btn, 1, 1)

        self.setLayout(layout)
        self.cargar()

    def cargar(self):
        dinero = sistema.total_dinero_vendido()
        productos = sistema.total_productos()
        stock_bajo = len(sistema.productos_stock_bajo())

        self.lbl_dinero.setText(f"💰 Ventas totales: ${dinero}")
        self.lbl_prod.setText(f"📦 Productos registrados: {productos}")
        self.lbl_stock.setText(f"⚠ Productos con stock bajo: {stock_bajo}")



# =========================
# ADMINISTRAR USUARIOS
# =========================
class VentanaUsuarios(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Usuarios 👤")
        self.resize(500,400)

        layout = QtWidgets.QVBoxLayout()

        
        self.tabla = QtWidgets.QTableWidget()
        layout.addWidget(self.tabla)

        
        btn_crear = QtWidgets.QPushButton("Crear usuario ➕👤")
        btn_crear.clicked.connect(self.crear_usuario)

        btn_eliminar = QtWidgets.QPushButton("Eliminar usuario ❌👤")
        btn_eliminar.clicked.connect(self.eliminar_usuario)

        layout.addWidget(btn_crear)
        layout.addWidget(btn_eliminar)

        self.setLayout(layout)
        self.cargar()

    def cargar(self):
        datos = sistema.obtener_usuarios()

        self.tabla.setRowCount(len(datos))
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["ID","Usuario","Rol"])

        for fila, user in enumerate(datos):
            for col, val in enumerate(user):
                self.tabla.setItem(fila, col,
                    QtWidgets.QTableWidgetItem(str(val)))

    def crear_usuario(self):
        usuario, ok = QtWidgets.QInputDialog.getText(self,"Usuario","Nombre:")
        if not ok: return

        password, ok = QtWidgets.QInputDialog.getText(self,"Password","Contraseña:")
        if not ok: return

        rol, ok = QtWidgets.QInputDialog.getItem(
            self,"Rol","Rol:",["admin","caja"],0,False)
        if not ok: return

        try:
            sistema.crear_usuario(usuario,password,rol)
            QtWidgets.QMessageBox.information(self,"OK","Usuario creado")
            self.cargar()
        except:
            QtWidgets.QMessageBox.warning(self,"Error","Usuario ya existe")

    def eliminar_usuario(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            return

        id_user = self.tabla.item(fila,0).text()

        sistema.eliminar_usuario(id_user)
        QtWidgets.QMessageBox.information(self,"OK","Usuario eliminado")
        self.cargar()

# =========================
# VENTANA VENTAS
# =========================
class VentanaVenta(QtWidgets.QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Nueva venta")
        self.resize(800,500)

        self.carrito = []
        self.total = 0

        layout = QtWidgets.QVBoxLayout()

        self.tabla_productos = QtWidgets.QTableWidget()
        self.tabla_productos.setColumnCount(5)
        self.tabla_productos.setHorizontalHeaderLabels(
            ["ID","Código","Nombre","Stock","Precio"]
        )
        layout.addWidget(self.tabla_productos)

        btn_agregar = QtWidgets.QPushButton("Agregar al carrito")
        btn_agregar.clicked.connect(self.agregar_producto)
        layout.addWidget(btn_agregar)

        self.tabla_carrito = QtWidgets.QTableWidget()
        self.tabla_carrito.setColumnCount(4)
        self.tabla_carrito.setHorizontalHeaderLabels(
            ["Producto","Cantidad","Precio","Subtotal"]
        )
        layout.addWidget(self.tabla_carrito)

        self.lbl_total = QtWidgets.QLabel("TOTAL: $0")
        layout.addWidget(self.lbl_total)

        btn_finalizar = QtWidgets.QPushButton("Finalizar venta")
        btn_finalizar.clicked.connect(self.finalizar_venta)
        layout.addWidget(btn_finalizar)

        self.setLayout(layout)
        self.cargar_productos()

    def cargar_productos(self):
        datos = sistema.obtener_inventario()
        self.tabla_productos.setRowCount(len(datos))

        for fila, p in enumerate(datos):
            for col, val in enumerate(p):
                self.tabla_productos.setItem(
                    fila, col, QtWidgets.QTableWidgetItem(str(val))
                )

    def agregar_producto(self):
        fila = self.tabla_productos.currentRow()
        if fila == -1:
            return

        codigo = self.tabla_productos.item(fila,1).text()
        prod = sistema.obtener_producto_por_codigo(codigo)[0]

        idp, nombre, precio, stock = prod

        cantidad, ok = QtWidgets.QInputDialog.getInt(
            self,"Cantidad","Cantidad:",1,1,stock)
        if not ok: return

        subtotal = cantidad * precio
        self.total += subtotal
        self.carrito.append((idp,nombre,cantidad,precio,subtotal))
        self.actualizar_carrito()

    def actualizar_carrito(self):
        self.tabla_carrito.setRowCount(len(self.carrito))

        for fila, item in enumerate(self.carrito):
            _, nombre, cant, precio, sub = item
            for col, val in enumerate([nombre,cant,precio,sub]):
                self.tabla_carrito.setItem(
                    fila, col, QtWidgets.QTableWidgetItem(str(val))
                )

        self.lbl_total.setText(f"TOTAL: ${self.total}")

    def finalizar_venta(self):
        if not self.carrito:
            return

        sistema.registrar_venta(self.usuario, self.carrito, self.total)
        QtWidgets.QMessageBox.information(self,"Venta","Venta realizada")

        self.carrito.clear()
        self.total = 0
        self.actualizar_carrito()
        self.cargar_productos()

# =========================
# ADMINISTRAR INVENTARIO
# =========================
class VentanaAdminInventario(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Administrar Inventario")
        self.resize(900,500)

        layout = QtWidgets.QVBoxLayout()
        self.tabla = QtWidgets.QTableWidget()
        layout.addWidget(self.tabla)

        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["ID","Código","Nombre","Cantidad","Unidad","Precio"]
        )
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        btn_agregar = QtWidgets.QPushButton("Nuevo producto")
        btn_agregar.clicked.connect(self.agregar_producto)

        btn_editar = QtWidgets.QPushButton("Editar producto")
        btn_editar.clicked.connect(self.editar_producto)

        btn_eliminar = QtWidgets.QPushButton("Eliminar producto")
        btn_eliminar.clicked.connect(self.eliminar_producto)

        layout.addWidget(btn_agregar)
        layout.addWidget(btn_editar)
        layout.addWidget(btn_eliminar)

        self.setLayout(layout)
        self.cargar()

    
    def cargar(self):
        datos = sistema.obtener_inventario()
        self.tabla.setRowCount(len(datos))

        for fila, producto in enumerate(datos):
            for col, valor in enumerate(producto):
                self.tabla.setItem(fila, col, QtWidgets.QTableWidgetItem(str(valor)))

    
    def agregar_producto(self):
        codigo, ok = QtWidgets.QInputDialog.getText(self,"Código","Código:")
        if not ok or not codigo: return

        nombre, ok = QtWidgets.QInputDialog.getText(self,"Nombre","Nombre:")
        if not ok or not nombre: return

        cantidad, ok = QtWidgets.QInputDialog.getInt(self,"Cantidad","Cantidad:",1,0)
        if not ok: return

        precio, ok = QtWidgets.QInputDialog.getDouble(self,"Precio","Precio:",0,0)
        if not ok: return

        stock_min, ok = QtWidgets.QInputDialog.getInt(self,"Stock mínimo","Stock mínimo:",1,0)
        if not ok: return

        try:
            sistema.agregar_producto_simple(codigo,nombre,cantidad,precio,stock_min)
            QtWidgets.QMessageBox.information(self,"OK","Producto creado")
            self.cargar()
        except:
            QtWidgets.QMessageBox.warning(self,"Error","El código ya existe")

    
    def editar_producto(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            QtWidgets.QMessageBox.warning(self,"Error","Selecciona un producto")
            return

        idp = int(self.tabla.item(fila,0).text())

        nombre, ok = QtWidgets.QInputDialog.getText(self,"Nombre","Nuevo nombre:")
        if not ok: return

        cantidad, ok = QtWidgets.QInputDialog.getInt(self,"Cantidad","Cantidad:",1,0)
        if not ok: return

        precio, ok = QtWidgets.QInputDialog.getDouble(self,"Precio","Precio:",0,0)
        if not ok: return

        stock_min, ok = QtWidgets.QInputDialog.getInt(self,"Stock mínimo","Stock mínimo:",1,0)
        if not ok: return

        codigo = self.tabla.item(fila,1).text()

        datos = (
            codigo, nombre, "", "General",
            cantidad, "pz", 0, precio,
            "activo", stock_min, idp
        )

        sistema.actualizar_producto(datos)
        QtWidgets.QMessageBox.information(self,"OK","Producto actualizado")
        self.cargar()

    
    def eliminar_producto(self):
        fila = self.tabla.currentRow()
        if fila == -1: return

        idp = int(self.tabla.item(fila,0).text())

        resp = QtWidgets.QMessageBox.question(self,"Confirmar","¿Eliminar producto?")
        if resp == QtWidgets.QMessageBox.Yes:
            sistema.eliminar_producto(idp)
            self.cargar()


# =========================
# EJECUTAR APP
# =========================
app = QtWidgets.QApplication(sys.argv)
window = LoginWindow()
window.show()
sys.exit(app.exec_())