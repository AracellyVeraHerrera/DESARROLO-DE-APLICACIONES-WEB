# Create a complete, runnable Python script for the inventory system and a README.
from textwrap import dedent

code = dedent('''
    """
    Sistema Avanzado de Gestión de Inventario (Consola + SQLite)
    Proyecto de ejemplo: Ferretería/Librería/Panadería (puedes adaptarlo)
    
    Requisitos cubiertos:
    - POO con clases Producto e Inventario
    - Uso de colecciones (dict, list, set, tuple) para optimizar operaciones
    - CRUD completo conectado a SQLite
    - Menú interactivo por consola
    - Código comentado y organizado
    """
    from __future__ import annotations
    import sqlite3
    from dataclasses import dataclass, field
    from typing import Dict, List, Optional, Tuple
    
    
    # ----------------------------
    # Modelo de dominio (POO)
    # ----------------------------
    @dataclass(eq=True, frozen=False)
    class Producto:
        id: int
        nombre: str
        cantidad: int
        precio: float
    
        # Getters/Setters explícitos (además de dataclass) para cumplir el requisito
        def get_id(self) -> int:
            return self.id
    
        def set_id(self, nuevo_id: int) -> None:
            self.id = nuevo_id
    
        def get_nombre(self) -> str:
            return self.nombre
    
        def set_nombre(self, nuevo_nombre: str) -> None:
            self.nombre = nuevo_nombre
    
        def get_cantidad(self) -> int:
            return self.cantidad
    
        def set_cantidad(self, nueva_cantidad: int) -> None:
            self.cantidad = nueva_cantidad
    
        def get_precio(self) -> float:
            return self.precio
    
        def set_precio(self, nuevo_precio: float) -> None:
            self.precio = nuevo_precio
    
        def __str__(self) -> str:
            return f"[{self.id}] {self.nombre} | Cantidad: {self.cantidad} | Precio: ${self.precio:.2f}"
    
    
    # ----------------------------
    # Repositorio + Servicio
    # ----------------------------
    class Inventario:
        """
        Maneja productos en memoria con un diccionario y persiste en SQLite.
        - Colecciones usadas:
            - dict[int, Producto] como caché en memoria para búsqueda O(1) por ID
            - list[Producto] para devolver listados ordenados
            - set[str] para validar unicidad rápida de nombres (opcional)
            - tuple para respuestas inmutables desde DB
        """
    
        def __init__(self, ruta_db: str = "inventario.db") -> None:
            self.ruta_db = ruta_db
            self._conn = sqlite3.connect(self.ruta_db)
            self._conn.execute("PRAGMA foreign_keys = ON;")
            self._crear_tabla_si_no_existe()
    
            # Caché: id -> Producto (colección base para O(1) por ID)
            self._cache: Dict[int, Producto] = {}
            # Set de nombres para chequeo rápido de duplicados
            self._nombres: set[str] = set()
            self._cargar_cache_desde_db()
    
        # --- Infraestructura SQLite ---
        def _crear_tabla_si_no_existe(self) -> None:
            sql = """
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL UNIQUE,
                cantidad INTEGER NOT NULL CHECK (cantidad >= 0),
                precio REAL NOT NULL CHECK (precio >= 0)
            );
            """
            self._conn.execute(sql)
            self._conn.commit()
    
        def _cargar_cache_desde_db(self) -> None:
            cur = self._conn.execute("SELECT id, nombre, cantidad, precio FROM productos;")
            filas: List[Tuple[int, str, int, float]] = cur.fetchall()
            for (pid, nombre, cantidad, precio) in filas:
                p = Producto(pid, nombre, cantidad, precio)
                self._cache[pid] = p
                self._nombres.add(nombre.lower())
    
        # --- CRUD ---
        def anadir_producto(self, producto: Producto) -> None:
            # Validaciones básicas
            if producto.id in self._cache:
                raise ValueError(f"Ya existe un producto con ID {producto.id}.")
            if producto.nombre.lower() in self._nombres:
                raise ValueError(f"Ya existe un producto con nombre '{producto.nombre}'.")
            if producto.cantidad < 0 or producto.precio < 0:
                raise ValueError("Cantidad y precio deben ser no negativos.")
    
            with self._conn:
                self._conn.execute(
                    "INSERT INTO productos (id, nombre, cantidad, precio) VALUES (?, ?, ?, ?);",
                    (producto.id, producto.nombre, producto.cantidad, producto.precio),
                )
            # Actualizar colecciones en memoria
            self._cache[producto.id] = producto
            self._nombres.add(producto.nombre.lower())
    
        def eliminar_por_id(self, product_id: int) -> bool:
            if product_id not in self._cache:
                return False
            nombre_borrar = self._cache[product_id].nombre.lower()
            with self._conn:
                self._conn.execute("DELETE FROM productos WHERE id = ?;", (product_id,))
            # Actualizar colecciones
            del self._cache[product_id]
            # Solo quitar el nombre si no hay otro con el mismo (no debería por UNIQUE)
            if nombre_borrar in self._nombres:
                self._nombres.remove(nombre_borrar)
            return True
    
        def actualizar_cantidad(self, product_id: int, nueva_cantidad: int) -> bool:
            if product_id not in self._cache:
                return False
            if nueva_cantidad < 0:
                raise ValueError("La cantidad no puede ser negativa.")
            with self._conn:
                self._conn.execute(
                    "UPDATE productos SET cantidad = ? WHERE id = ?;",
                    (nueva_cantidad, product_id),
                )
            self._cache[product_id].set_cantidad(nueva_cantidad)
            return True
    
        def actualizar_precio(self, product_id: int, nuevo_precio: float) -> bool:
            if product_id not in self._cache:
                return False
            if nuevo_precio < 0:
                raise ValueError("El precio no puede ser negativo.")
            with self._conn:
                self._conn.execute(
                    "UPDATE productos SET precio = ? WHERE id = ?;",
                    (nuevo_precio, product_id),
                )
            self._cache[product_id].set_precio(nuevo_precio)
            return True
    
        def buscar_por_nombre(self, termino: str) -> List[Producto]:
            """
            Búsqueda flexible (LIKE) en DB, retorna lista de coincidencias.
            También podría hacerse sobre self._cache con comprensión de listas.
            """
            like = f"%{termino.lower()}%"
            cur = self._conn.execute(
                "SELECT id, nombre, cantidad, precio FROM productos WHERE lower(nombre) LIKE ? ORDER BY nombre;",
                (like,),
            )
            resultados = [Producto(pid, nom, cant, prec) for pid, nom, cant, prec in cur.fetchall()]
            return resultados
    
        def mostrar_todos(self) -> List[Producto]:
            # Devolvemos una lista ordenada por id desde la caché
            return [self._cache[k] for k in sorted(self._cache.keys())]
    
        def cerrar(self) -> None:
            self._conn.close()
    
    
    # ----------------------------
    # Interfaz de Usuario (Consola)
    # ----------------------------
    def imprimir_menu() -> None:
        print("\\n=== SISTEMA DE INVENTARIO ===")
        print("1. Añadir producto")
        print("2. Eliminar producto por ID")
        print("3. Actualizar cantidad de un producto")
        print("4. Actualizar precio de un producto")
        print("5. Buscar productos por nombre")
        print("6. Mostrar todos los productos")
        print("7. Cargar datos de ejemplo (opcional)")
        print("0. Salir")
    
    def pedir_int(mensaje: str) -> int:
        while True:
            try:
                return int(input(mensaje))
            except ValueError:
                print("Entrada inválida. Debe ser un número entero.")
    
    def pedir_float(mensaje: str) -> float:
        while True:
            try:
                return float(input(mensaje))
            except ValueError:
                print("Entrada inválida. Debe ser un número (usa punto decimal).")
    
    def cargar_datos_demo(inv: Inventario) -> None:
        demo = [
            Producto(1, "Martillo", 25, 6.5),
            Producto(2, "Clavos (100u)", 100, 3.0),
            Producto(3, "Destornillador", 40, 4.75),
            Producto(4, "Serrucho", 10, 12.99),
        ]
        agregados = 0
        for p in demo:
            try:
                inv.anadir_producto(p)
                agregados += 1
            except Exception as e:
                # Evitar detener la carga si ya existen
                pass
        print(f"Se cargaron {agregados} productos de ejemplo (los duplicados fueron ignorados).")
    
    def main() -> None:
        inventario = Inventario()  # inventario.db en la carpeta actual
        try:
            while True:
                imprimir_menu()
                opcion = input("Selecciona una opción: ").strip()
    
                if opcion == "1":
                    pid = pedir_int("ID (entero, único): ")
                    nombre = input("Nombre: ").strip()
                    cantidad = pedir_int("Cantidad: ")
                    precio = pedir_float("Precio: ")
                    try:
                        inventario.anadir_producto(Producto(pid, nombre, cantidad, precio))
                        print("Producto añadido correctamente.")
                    except Exception as e:
                        print(f"Error: {e}")
    
                elif opcion == "2":
                    pid = pedir_int("ID a eliminar: ")
                    if inventario.eliminar_por_id(pid):
                        print("Producto eliminado.")
                    else:
                        print("No existe un producto con ese ID.")
    
                elif opcion == "3":
                    pid = pedir_int("ID del producto: ")
                    nueva_cantidad = pedir_int("Nueva cantidad: ")
                    try:
                        if inventario.actualizar_cantidad(pid, nueva_cantidad):
                            print("Cantidad actualizada.")
                        else:
                            print("No existe un producto con ese ID.")
                    except Exception as e:
                        print(f"Error: {e}")
    
                elif opcion == "4":
                    pid = pedir_int("ID del producto: ")
                    nuevo_precio = pedir_float("Nuevo precio: ")
                    try:
                        if inventario.actualizar_precio(pid, nuevo_precio):
                            print("Precio actualizado.")
                        else:
                            print("No existe un producto con ese ID.")
                    except Exception as e:
                        print(f"Error: {e}")
    
                elif opcion == "5":
                    termino = input("Buscar por nombre (subcadena): ").strip()
                    resultados = inventario.buscar_por_nombre(termino)
                    if resultados:
                        print("\\n-- Resultados --")
                        for p in resultados:
                            print(p)
                    else:
                        print("Sin coincidencias.")
    
                elif opcion == "6":
                    productos = inventario.mostrar_todos()
                    if productos:
                        print("\\n-- Inventario --")
                        for p in productos:
                            print(p)
                    else:
                        print("Inventario vacío.")
    
                elif opcion == "7":
                    cargar_datos_demo(inventario)
    
                elif opcion == "0":
                    print("Saliendo...")
                    break
                else:
                    print("Opción no válida.")
        finally:
            inventario.cerrar()
    
    
    if __name__ == "__main__":
        main()
''')

readme = dedent('''
    # Sistema Avanzado de Gestión de Inventario (Python + SQLite)
    
    Este proyecto implementa un sistema de inventario en consola utilizando Programación Orientada a Objetos (POO), colecciones de Python y persistencia en SQLite.
    
    ## Características
    - **Clases**: `Producto` e `Inventario` (POO).
    - **Colecciones**:
      - `dict[int, Producto]` como caché en memoria para búsquedas O(1) por ID.
      - `set[str]` para validar unicidad de nombres rápidamente.
      - `list[Producto]` para listados ordenados.
      - `tuple` desde consultas a SQLite para datos inmutables.
    - **CRUD** completo: añadir, eliminar, actualizar cantidad y precio, buscar por nombre y mostrar todo.
    - **SQLite**: creación automática de la tabla `productos` (si no existe) y sincronización con la caché en memoria.
    - **Menú de consola**: interfaz simple y robusta.
    
    ## Requisitos
    - Python 3.10+
    - No depende de paquetes externos. Usa la librería estándar (`sqlite3`, `dataclasses`, etc.).
    
    ## Cómo ejecutar
    ```bash
    # 1) (Opcional) Crear y activar un entorno virtual
    python -m venv .venv
    # Windows: .venv\\Scripts\\activate
    # Linux/Mac: source .venv/bin/activate
    
    # 2) Ejecutar el programa
    python inventario_sqlite.py
    ```
    
    Al ejecutarse, se creará el archivo `inventario.db` en la carpeta actual. Usa el menú para añadir, eliminar, actualizar, buscar y listar productos. Opción **7** carga datos de ejemplo.
    
    ## Diseño y Decisiones
    - **Capa de caché** (`dict`): permite respuestas instantáneas en operaciones por ID y reduce consultas repetidas a SQLite.
    - **Integridad y validaciones**: se aplica `UNIQUE` sobre `nombre` y `PRIMARY KEY` sobre `id`, con `CHECK` para evitar valores negativos.
    - **Transacciones**: se utilizan context managers (`with self._conn:`) para asegurar atomicidad y confirmación de cambios.
    - **Búsqueda flexible**: `LIKE` con `lower()` en la base de datos para encontrar subcadenas sin distinguir mayúsculas/minúsculas.
    
    ## Estructura del Código
    - `Producto`: modelo con getters/setters para cumplir el requisito explícito y `__str__` para impresión bonita.
    - `Inventario`: servicio/repositorio que expone métodos CRUD y maneja sincronización entre DB y caché.
    - `main()`: menú y validaciones de entrada.
    
    ## Pruebas Manuales Sugeridas
    1. Añadir un producto nuevo (ID único) y verificar que aparece en "Mostrar todos".
    2. Intentar añadir un ID o nombre duplicado: debe mostrar error.
    3. Actualizar cantidad y precio; confirmar los cambios con "Mostrar todos".
    4. Buscar por subcadena del nombre (p. ej., "clav").
    5. Eliminar por ID y verificar que desaparece.
    
    ## Subir a GitHub
    1. Crea un repositorio nuevo (p. ej., `inventario-sqlite-poo`).
    2. Sube los archivos `inventario_sqlite.py`, `inventario.db` (opcional; se recrea solo), y `README.md`.
    3. Copia el enlace del repositorio en Moodle.
    
    ## Extensiones Opcionales
    - Exportar/Importar a CSV.
    - Reportes (total de items, valor total de inventario).
    - Separar capas en módulos (`models.py`, `repository.py`, `menu.py`).
    - Añadir pruebas unitarias con `pytest`.
    - Renderizar una versión web simple con `Flask` o `FastAPI` (Opcional "Render").
''')

with open('/mnt/data/inventario_sqlite.py', 'w', encoding='utf-8') as f:
    f.write(code)

with open('/mnt/data/README.md', 'w', encoding='utf-8') as f:
    f.write(readme)

'/mnt/data/inventario_sqlite.py y /mnt/data/README.md creados correctamente.'
