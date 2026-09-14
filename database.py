import sqlite3
from pathlib import Path
import sys


# ============================================================
# RUTAS LOCALES DE LA APLICACIÓN
# ============================================================

APP_NAME = "MiColeccion"

if getattr(sys, "frozen", False):
    # Cuando sea un .exe
    BASE_DIR = Path.home() / "AppData" / "Local" / APP_NAME
else:
    # Durante desarrollo
    BASE_DIR = Path(__file__).resolve().parent / "data"

BASE_DIR.mkdir(parents=True, exist_ok=True)

IMAGES_DIR = BASE_DIR / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = BASE_DIR / "coleccion.db"


# ============================================================
# CONEXIÓN
# ============================================================

def conectar():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row

    # SQLite no activa las foreign keys por defecto.
    conexion.execute("PRAGMA foreign_keys = ON")

    return conexion


# ============================================================
# CREACIÓN Y MIGRACIÓN DE TABLAS
# ============================================================

def crear_tablas():

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Listas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            orden INTEGER NOT NULL DEFAULT 0,
            is_blurred INTEGER NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tarjetas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_lista INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            descripcion TEXT DEFAULT '',
            url TEXT DEFAULT '',
            foto_ruta TEXT DEFAULT '',
            precio REAL,
            moneda TEXT,
            estado TEXT NOT NULL DEFAULT 'normal',
            is_blurred INTEGER NOT NULL DEFAULT 0,
            orden INTEGER NOT NULL DEFAULT 0,

            FOREIGN KEY (id_lista)
            REFERENCES Listas(id)
            ON DELETE CASCADE
        )
    """)

    conexion.commit()

    # Migraciones para bases antiguas.
    migrar_base_datos(conexion)

    conexion.close()


def migrar_base_datos(conexion):

    cursor = conexion.cursor()

    # ----------------------------
    # Columnas de Tarjetas
    # ----------------------------

    cursor.execute("PRAGMA table_info(Tarjetas)")
    columnas_tarjetas = {
        fila["name"]
        for fila in cursor.fetchall()
    }

    nuevas_columnas_tarjetas = {

        "descripcion":
            "TEXT DEFAULT ''",

        "url":
            "TEXT DEFAULT ''",

        "orden":
            "INTEGER NOT NULL DEFAULT 0"

    }

    for nombre, tipo in nuevas_columnas_tarjetas.items():

        if nombre not in columnas_tarjetas:

            cursor.execute(
                f"""
                ALTER TABLE Tarjetas
                ADD COLUMN {nombre} {tipo}
                """
            )

    # ----------------------------
    # Columnas de Listas
    # ----------------------------

    cursor.execute("PRAGMA table_info(Listas)")

    columnas_listas = {
        fila["name"]
        for fila in cursor.fetchall()
    }

    if "is_blurred" not in columnas_listas:

        cursor.execute("""
            ALTER TABLE Listas
            ADD COLUMN is_blurred
            INTEGER NOT NULL DEFAULT 0
        """)

    conexion.commit()

    # Corregir orden inicial si una BD antigua tiene todo en 0.
    normalizar_ordenes()


# ============================================================
# NORMALIZAR ÓRDENES
# ============================================================

def normalizar_ordenes():

    conexion = conectar()
    cursor = conexion.cursor()

    # ----------------------------
    # Listas
    # ----------------------------

    cursor.execute("""
        SELECT id
        FROM Listas
        ORDER BY orden ASC, id ASC
    """)

    listas = cursor.fetchall()

    for indice, lista in enumerate(listas):

        cursor.execute("""
            UPDATE Listas
            SET orden = ?
            WHERE id = ?
        """, (
            indice,
            lista["id"]
        ))

    # ----------------------------
    # Tarjetas
    # ----------------------------

    cursor.execute("""
        SELECT id
        FROM Listas
        ORDER BY orden ASC
    """)

    listas = cursor.fetchall()

    for lista in listas:

        cursor.execute("""
            SELECT id
            FROM Tarjetas
            WHERE id_lista = ?
            ORDER BY orden ASC, id ASC
        """, (
            lista["id"],
        ))

        tarjetas = cursor.fetchall()

        for indice, tarjeta in enumerate(tarjetas):

            cursor.execute("""
                UPDATE Tarjetas
                SET orden = ?
                WHERE id = ?
            """, (
                indice,
                tarjeta["id"]
            ))

    conexion.commit()
    conexion.close()


# ============================================================
# LISTAS
# ============================================================

def crear_lista(nombre):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM Listas
    """)

    orden = cursor.fetchone()["total"]

    cursor.execute("""
        INSERT INTO Listas (
            nombre,
            orden
        )
        VALUES (?, ?)
    """, (
        nombre.strip(),
        orden
    ))

    conexion.commit()

    nuevo_id = cursor.lastrowid

    conexion.close()

    return nuevo_id


def obtener_listas():

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *
        FROM Listas
        ORDER BY orden ASC, id ASC
    """)

    listas = cursor.fetchall()

    conexion.close()

    return listas


def obtener_lista(id_lista):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *
        FROM Listas
        WHERE id = ?
    """, (
        id_lista,
    ))

    lista = cursor.fetchone()

    conexion.close()

    return lista


def actualizar_lista(
    id_lista,
    nombre
):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE Listas
        SET nombre = ?
        WHERE id = ?
    """, (
        nombre.strip(),
        id_lista
    ))

    conexion.commit()
    conexion.close()


def eliminar_lista(id_lista):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM Listas
        WHERE id = ?
    """, (
        id_lista,
    ))

    conexion.commit()
    conexion.close()

    normalizar_ordenes()


# ============================================================
# TARJETAS
# ============================================================

def crear_tarjeta(
    id_lista,
    titulo,
    descripcion="",
    url="",
    foto_ruta="",
    precio=None,
    moneda=None,
    estado="normal",
    is_blurred=False
):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM Tarjetas
        WHERE id_lista = ?
    """, (
        id_lista,
    ))

    orden = cursor.fetchone()["total"]

    cursor.execute("""
        INSERT INTO Tarjetas (
            id_lista,
            titulo,
            descripcion,
            url,
            foto_ruta,
            precio,
            moneda,
            estado,
            is_blurred,
            orden
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        id_lista,
        titulo.strip(),
        descripcion.strip(),
        url.strip(),
        foto_ruta,
        precio,
        moneda,
        estado,
        int(is_blurred),
        orden
    ))

    conexion.commit()

    nuevo_id = cursor.lastrowid

    conexion.close()

    return nuevo_id


def obtener_tarjetas_por_lista(id_lista):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *
        FROM Tarjetas
        WHERE id_lista = ?
        ORDER BY orden ASC, id ASC
    """, (
        id_lista,
    ))

    tarjetas = cursor.fetchall()

    conexion.close()

    return tarjetas


def obtener_tarjeta(id_tarjeta):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *
        FROM Tarjetas
        WHERE id = ?
    """, (
        id_tarjeta,
    ))

    tarjeta = cursor.fetchone()

    conexion.close()

    return tarjeta


def actualizar_tarjeta(
    id_tarjeta,
    titulo,
    descripcion,
    url,
    foto_ruta,
    precio,
    moneda,
    estado
):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE Tarjetas
        SET
            titulo = ?,
            descripcion = ?,
            url = ?,
            foto_ruta = ?,
            precio = ?,
            moneda = ?,
            estado = ?
        WHERE id = ?
    """, (
        titulo.strip(),
        descripcion.strip(),
        url.strip(),
        foto_ruta,
        precio,
        moneda,
        estado,
        id_tarjeta
    ))

    conexion.commit()
    conexion.close()


def eliminar_tarjeta(id_tarjeta):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id_lista
        FROM Tarjetas
        WHERE id = ?
    """, (
        id_tarjeta,
    ))

    tarjeta = cursor.fetchone()

    if tarjeta is None:

        conexion.close()
        return

    id_lista = tarjeta["id_lista"]

    cursor.execute("""
        DELETE FROM Tarjetas
        WHERE id = ?
    """, (
        id_tarjeta,
    ))

    conexion.commit()
    conexion.close()

    reordenar_tarjetas(
        id_lista,
        obtener_ids_tarjetas(id_lista)
    )


# ============================================================
# DRAG & DROP
# ============================================================

def obtener_ids_tarjetas(id_lista):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id
        FROM Tarjetas
        WHERE id_lista = ?
        ORDER BY orden ASC, id ASC
    """, (
        id_lista,
    ))

    ids = [
        fila["id"]
        for fila in cursor.fetchall()
    ]

    conexion.close()

    return ids


def reordenar_tarjetas(
    id_lista,
    ids_tarjetas
):
    """
    Guarda el orden completo de las tarjetas
    de una lista.
    """

    conexion = conectar()
    cursor = conexion.cursor()

    for orden, id_tarjeta in enumerate(ids_tarjetas):

        cursor.execute("""
            UPDATE Tarjetas
            SET
                id_lista = ?,
                orden = ?
            WHERE id = ?
        """, (
            id_lista,
            orden,
            id_tarjeta
        ))

    conexion.commit()
    conexion.close()


def mover_tarjeta(
    id_tarjeta,
    id_lista_origen,
    id_lista_destino,
    nuevo_indice
):
    """
    Mueve una tarjeta entre listas o dentro
    de la misma lista.

    nuevo_indice:
        posición final dentro de la lista destino.
    """

    if id_lista_origen == id_lista_destino:

        ids = obtener_ids_tarjetas(
            id_lista_origen
        )

        if id_tarjeta not in ids:
            return

        indice_actual = ids.index(
            id_tarjeta
        )

        ids.pop(
            indice_actual
        )

        nuevo_indice = max(
            0,
            min(
                nuevo_indice,
                len(ids)
            )
        )

        ids.insert(
            nuevo_indice,
            id_tarjeta
        )

        reordenar_tarjetas(
            id_lista_origen,
            ids
        )

        return

    # ----------------------------
    # LISTA ORIGEN
    # ----------------------------

    ids_origen = obtener_ids_tarjetas(
        id_lista_origen
    )

    if id_tarjeta in ids_origen:

        ids_origen.remove(
            id_tarjeta
        )

    # ----------------------------
    # LISTA DESTINO
    # ----------------------------

    ids_destino = obtener_ids_tarjetas(
        id_lista_destino
    )

    nuevo_indice = max(
        0,
        min(
            nuevo_indice,
            len(ids_destino)
        )
    )

    ids_destino.insert(
        nuevo_indice,
        id_tarjeta
    )

    # Primero actualizar origen.
    reordenar_tarjetas(
        id_lista_origen,
        ids_origen
    )

    # Después destino.
    reordenar_tarjetas(
        id_lista_destino,
        ids_destino
    )


# ============================================================
# PRIVACIDAD
# ============================================================

def alternar_privacidad_tarjeta(
    id_tarjeta
):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE Tarjetas
        SET is_blurred =
            CASE
                WHEN is_blurred = 1
                THEN 0
                ELSE 1
            END
        WHERE id = ?
    """, (
        id_tarjeta,
    ))

    conexion.commit()
    conexion.close()


def alternar_privacidad_lista(
    id_lista
):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE Listas
        SET is_blurred =
            CASE
                WHEN is_blurred = 1
                THEN 0
                ELSE 1
            END
        WHERE id = ?
    """, (
        id_lista,
    ))

    conexion.commit()
    conexion.close()


# ============================================================
# INICIALIZACIÓN
# ============================================================

crear_tablas()