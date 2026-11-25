# Nexo Abasto: prototipo breve para inventario, ventas y distribución.
# Ejemplo académico en Python 3. Los comentarios señalan los temas de clase y
# los requerimientos atendidos. Solo usa estructuras y funciones de Python.


# Árbol binario de búsqueda (BST) y recursividad para organizar el catálogo.
class NodoProducto:
    def __init__(self, codigo):
        self.codigo = codigo
        self.izquierdo = None
        self.derecho = None


class Catalogo:
    def __init__(self):
        self.raiz = None

    def insertar(self, codigo):
        # Caso base: encontramos un espacio vacío para el nuevo nodo.
        if self.raiz is None:
            self.raiz = NodoProducto(codigo)
        else:
            self._insertar_desde(self.raiz, codigo)

    def _insertar_desde(self, nodo, codigo):
        # Caso recursivo: menor a la izquierda, mayor a la derecha.
        if codigo < nodo.codigo:
            if nodo.izquierdo is None:
                nodo.izquierdo = NodoProducto(codigo)
            else:
                self._insertar_desde(nodo.izquierdo, codigo)
        elif codigo > nodo.codigo:
            if nodo.derecho is None:
                nodo.derecho = NodoProducto(codigo)
            else:
                self._insertar_desde(nodo.derecho, codigo)

    def buscar(self, nodo, codigo):
        # Recorrido recursivo por la regla de orden del BST.
        if nodo is None or nodo.codigo == codigo:  # caso base
            return nodo
        if codigo < nodo.codigo:
            return self.buscar(nodo.izquierdo, codigo)
        return self.buscar(nodo.derecho, codigo)

    def listar_en_orden(self, nodo):
        # Recorrido inorden: izquierda, raíz, derecha.
        if nodo is None:  # caso base
            return []
        return (self.listar_en_orden(nodo.izquierdo) + [nodo.codigo]
                + self.listar_en_orden(nodo.derecho))


# Rutas de distribución mediante grafos con lista de adyacencia.
class RedDistribucion:
    def __init__(self):
        self.vecinos = {
            "Bodega Central": ["Bodega Regional", "Sucursal Norte",
                               "Sucursal Sur", "Sucursal Este"],
            "Bodega Regional": ["Bodega Central", "Sucursal Oeste"],
            "Sucursal Norte": ["Bodega Central", "Sucursal Oeste"],
            "Sucursal Sur": ["Bodega Central", "Sucursal Oeste"],
            "Sucursal Este": ["Bodega Central", "Sucursal Oeste"],
            "Sucursal Oeste": ["Bodega Regional", "Sucursal Norte",
                               "Sucursal Sur", "Sucursal Este"],
        }

    # Cálculo de rutas posibles entre bodegas y sucursales.
    def buscar_ruta(self, origen, destino, visitados=None):
        if origen not in self.vecinos or destino not in self.vecinos:
            return []
        if origen == destino:
            return [origen]
        if visitados is None:
            visitados = []
        visitados = visitados + [origen]
        for sucursal in self.vecinos[origen]:
            if sucursal not in visitados:
                ruta = self.buscar_ruta(sucursal, destino, visitados)
                if ruta:
                    return [origen] + ruta
        return []


# Datos iniciales del sistema: bodegas, sucursales, productos y existencias.
BODEGAS = ["Bodega Central", "Bodega Regional"]
SUCURSALES = ["Sucursal Norte", "Sucursal Sur", "Sucursal Este", "Sucursal Oeste"]
productos = {
    1001: {"nombre": "Arroz 1 kg", "categoria": "Granos", "precio": 1.25,
           "proveedor": "Distribuidora Central"},
    1002: {"nombre": "Leche 1 L", "categoria": "Lácteos", "precio": 1.10,
           "proveedor": "Lácteos La Vaquita"},
    1003: {"nombre": "Huevos (docena)", "categoria": "Refrigerados", "precio": 2.40,
           "proveedor": "Granja El Sol"},
    1004: {"nombre": "Aceite 750 ml", "categoria": "Despensa", "precio": 2.15,
           "proveedor": "Distribuidora Central"},
    1005: {"nombre": "Frijoles 1 kg", "categoria": "Granos", "precio": 1.60,
           "proveedor": "Granos del Valle"},
}
existencias = {
    "Bodega Central": {1001: 30, 1002: 24, 1003: 18, 1004: 20, 1005: 28},
    "Bodega Regional": {1001: 15, 1002: 12, 1003: 10, 1004: 14, 1005: 16},
    "Sucursal Norte": {1001: 8, 1002: 5, 1003: 4, 1004: 6, 1005: 7},
    "Sucursal Sur": {1001: 6, 1002: 4, 1003: 5, 1004: 3, 1005: 8},
    "Sucursal Este": {1001: 5, 1002: 6, 1003: 3, 1004: 4, 1005: 5},
    "Sucursal Oeste": {1001: 4, 1002: 3, 1003: 2, 1004: 5, 1005: 4},
}
proveedores = {"Distribuidora Central", "Lácteos La Vaquita",
               "Granja El Sol", "Granos del Valle"}
clientes = []
ventas = []                 # Listas para guardar registros en orden.
pedidos = []                # Cola FIFO implementada con lista.
historial_pedidos = []      # Conserva todos los pedidos y su estado actual.
ventas_para_anular = []     # Pila LIFO implementada con lista.
movimientos = []            # Historial sencillo de operaciones.
catalogo = Catalogo()
for codigo_producto in productos:
    catalogo.insertar(codigo_producto)
red = RedDistribucion()


# Consulta de catálogo e inventario por ubicación.
def mostrar_productos():
    codigos = catalogo.listar_en_orden(catalogo.raiz)
    print("\nCATÁLOGO DE PRODUCTOS")
    for codigo in codigos:
        ficha = productos[codigo]
        print(f"{codigo} | {ficha['nombre']} | {ficha['categoria']} | "
              f"{ficha['proveedor']} | ${ficha['precio']:.2f}")
    for titulo, ubicaciones in (("BODEGAS (almacenamiento)", BODEGAS),
                                ("SUCURSALES (tiendas)", SUCURSALES)):
        print(f"\n{titulo}")
        for ubicacion in ubicaciones:
            print(f"{ubicacion}:")
            for codigo in codigos:
                print(f"  {productos[codigo]['nombre']}: "
                      f"{existencias[ubicacion].get(codigo, 0)} unidades")


# Registro de nuevos productos en el catálogo.
def registrar_producto():
    try:
        codigo = int(input("Código del producto nuevo: "))
        nombre = input("Nombre del producto: ").strip()
        categoria = input("Categoría: ").strip()
        proveedor = input("Proveedor: ").strip()
        precio = float(input("Precio unitario: $"))
        cantidad = int(input("Cantidad inicial en Bodega Central: "))
        if codigo in productos or not nombre or not categoria or not proveedor:
            print("Ese código ya existe o dejaste algún dato obligatorio vacío.")
        elif precio <= 0 or cantidad < 0:
            print("Revisa los datos: el precio debe ser mayor a cero y el stock no puede ser negativo.")
        else:
            productos[codigo] = {"nombre": nombre, "categoria": categoria,
                                 "precio": precio, "proveedor": proveedor}
            for ubicacion in existencias:
                existencias[ubicacion][codigo] = 0
            existencias["Bodega Central"][codigo] = cantidad
            proveedores.add(proveedor)
            catalogo.insertar(codigo)  # el árbol también se actualiza
            movimientos.append(f"Producto agregado: {nombre} ({categoria})")
            print("Listo, el producto ya quedó guardado en el catálogo.")
    except ValueError:
        print("Asegúrate de poner números válidos en código, precio y cantidad.")


# Registro de ventas y descuento de existencias en sucursal.
def registrar_venta():
    try:
        nombre_cliente = input("Nombre del cliente: ").strip()
        sucursal = input("Sucursal (por ejemplo, Sucursal Norte): ").strip().title()
        codigo = int(input("Código del producto: "))
        cantidad = int(input("Cantidad a vender: "))
        if not nombre_cliente or sucursal not in SUCURSALES or catalogo.buscar(catalogo.raiz, codigo) is None:
            print("Revisa el cliente, la sucursal o el código del producto; algo no coincide.")
            return
        if cantidad <= 0 or existencias[sucursal].get(codigo, 0) < cantidad:
            print(f"No se puede hacer la venta: cantidad inválida o poco stock en {sucursal}.")
            return
        ficha = productos[codigo]
        total = cantidad * ficha["precio"]
        venta = {"cliente": nombre_cliente, "sucursal": sucursal, "codigo": codigo,
                 "cantidad": cantidad, "total": total}
        clientes.append(nombre_cliente)
        ventas.append(venta)
        ventas_para_anular.append(venta)  # apilar la última venta
        existencias[sucursal][codigo] -= cantidad
        movimientos.append(f"Venta en {sucursal}: {cantidad} {ficha['nombre']} a {nombre_cliente}")
        print(f"Venta registrada con éxito. Total a pagar: ${total:.2f}")
    except ValueError:
        print("Pon números enteros en el código y en la cantidad.")


# Registro de entradas de mercancía a bodega.
def registrar_entrada():
    try:
        bodega = input("Bodega que recibe (Bodega Central o Bodega Regional): ").strip().title()
        codigo = int(input("Código del producto que llegó: "))
        cantidad = int(input("Cantidad recibida: "))
        if bodega not in BODEGAS or codigo not in productos or cantidad <= 0:
            print("Verifica la bodega, el código del producto o la cantidad ingresada.")
            return
        existencias[bodega][codigo] = existencias[bodega].get(codigo, 0) + cantidad
        movimientos.append(f"Entrada de {cantidad} unidades de {productos[codigo]['nombre']} en {bodega}")
        print(f"Mercancía sumada en {bodega}.")
    except ValueError:
        print("El código y la cantidad tienen que ser números enteros.")


# Transferencias de inventario entre ubicaciones.
def transferir_existencias():
    try:
        origen = input("¿De dónde sale el stock? (origen): ").strip().title()
        destino = input("¿Hacia dónde va? (destino): ").strip().title()
        codigo = int(input("Código del producto: "))
        cantidad = int(input("Cantidad a mover: "))
        if origen not in existencias or destino not in existencias or origen == destino:
            print("Elige dos ubicaciones válidas y que sean distintas.")
        elif codigo not in productos or cantidad <= 0:
            print("El producto o la cantidad no son válidos.")
        elif existencias[origen].get(codigo, 0) < cantidad:
            print("No alcanza el stock en la ubicación de origen para esa transferencia.")
        else:
            existencias[origen][codigo] -= cantidad
            existencias[destino][codigo] = existencias[destino].get(codigo, 0) + cantidad
            movimientos.append(f"Transferencia {productos[codigo]['nombre']}: {origen} a {destino}")
            print("Transferencia completada.")
    except ValueError:
        print("El código y la cantidad tienen que ser números enteros.")


# Registro de pedidos de sucursales en la cola de espera.
def agregar_pedido():
    try:
        sucursal = input("Sucursal que pide (por ejemplo, Sucursal Norte): ").strip().title()
        codigo = int(input("Código del producto: "))
        cantidad = int(input("Cantidad solicitada: "))
        if sucursal not in SUCURSALES:
            print("Esa sucursal no está registrada.")
        elif codigo not in productos or cantidad <= 0:
            print("El producto o la cantidad no son válidos.")
        else:
            pedido = {"numero": len(historial_pedidos) + 1,
                      "sucursal": sucursal, "codigo": codigo,
                      "cantidad": cantidad, "estado": "Pendiente"}
            pedidos.append(pedido)  # entra al final de la cola
            historial_pedidos.append(pedido)
            movimientos.append(f"Pedido recibido para {sucursal}")
            print(f"Pedido anotado. Quedan {len(pedidos)} pendientes.")
    except ValueError:
        print("El código y la cantidad tienen que ser números enteros.")


# Despachos desde bodega y trazado de ruta hacia la sucursal.
def despachar_pedido():
    if not pedidos:
        print("Por ahora no hay pedidos pendientes.")
        return
    pedido = pedidos[0]
    sucursal = pedido["sucursal"]
    codigo = pedido["codigo"]
    cantidad = pedido["cantidad"]
    bodega = input("¿Desde qué bodega despachamos? (Bodega Central o Bodega Regional): ").strip().title()
    if bodega not in BODEGAS:
        print("Solo podés despachar desde una bodega válida.")
        return
    if existencias[bodega].get(codigo, 0) < cantidad:
        print(f"No hay suficiente stock en {bodega}; el pedido sigue esperando turno.")
        return
    ruta = red.buscar_ruta(bodega, sucursal)  # calcula la ruta del despacho
    pedidos.pop(0)  # sale de la cola el primero que ingresó
    pedido["estado"] = "Despachado"
    existencias[bodega][codigo] -= cantidad
    existencias[sucursal][codigo] = existencias[sucursal].get(codigo, 0) + cantidad
    movimientos.append(f"Despacho desde {bodega} a {sucursal}: {' → '.join(ruta)}")
    print(f"Se despachó {productos[codigo]['nombre']} x{cantidad} por la ruta: {' → '.join(ruta)}")


# Anulación de la última venta registrada.
def anular_ultima_venta():
    if not ventas_para_anular:
        print("No hay ninguna venta reciente para anular.")
        return
    venta = ventas_para_anular.pop()
    ventas.remove(venta)
    existencias[venta["sucursal"]][venta["codigo"]] += venta["cantidad"]
    movimientos.append("Se anuló la última venta")
    print("Listo, se anuló la última venta y volvió el stock a la sucursal.")


# Resumen general de existencias, ventas, pedidos y movimientos.
def ver_resumen():
    print("\nRESUMEN DE EXISTENCIAS POR UBICACIÓN")
    for titulo, ubicaciones in (("Bodegas", BODEGAS), ("Sucursales", SUCURSALES)):
        print(f"{titulo}:")
        for ubicacion in ubicaciones:
            stock_ubicacion = existencias[ubicacion]
            print(f"  {ubicacion}: {sum(stock_ubicacion.values())} unidades")
    print(f"Ventas registradas: {len(ventas)} | Pedidos pendientes: {len(pedidos)}")
    print(f"Clientes: {', '.join(sorted(set(clientes))) if clientes else 'ninguno'}")
    print(f"Proveedores: {', '.join(sorted(proveedores))}")
    print("Estados de pedidos:",
          ", ".join(f"#{p['numero']} {p['estado']}" for p in historial_pedidos)
          if historial_pedidos else "ninguno")
    print("Últimos movimientos:", movimientos[-5:] if movimientos else "ninguno")


# Menú principal del sistema.
def iniciar_sistema():
    while True:
        print("\nNEXO ABASTO | GESTIÓN INTEGRAL")
        print("1. Ver productos y existencias")
        print("2. Registrar producto, categoría y proveedor")
        print("3. Registrar entrada de proveedor")
        print("4. Transferir existencias entre ubicaciones")
        print("5. Registrar cliente y venta")
        print("6. Recibir pedido de sucursal")
        print("7. Despachar primer pedido (FIFO)")
        print("8. Anular última venta (pila)")
        print("9. Ver resumen y estados de pedidos")
        print("0. Salir")
        opcion = input("Elegí una opción: ").strip()
        if opcion == "1":
            mostrar_productos()
        elif opcion == "2":
            registrar_producto()
        elif opcion == "3":
            registrar_entrada()
        elif opcion == "4":
            transferir_existencias()
        elif opcion == "5":
            registrar_venta()
        elif opcion == "6":
            agregar_pedido()
        elif opcion == "7":
            despachar_pedido()
        elif opcion == "8":
            anular_ultima_venta()
        elif opcion == "9":
            ver_resumen()
        elif opcion == "0":
            print("Sistema cerrado. ¡Gracias!")
            break
        else:
            print("Esa opción no existe; elegí un número del menú.")


if __name__ == "__main__":
    iniciar_sistema()