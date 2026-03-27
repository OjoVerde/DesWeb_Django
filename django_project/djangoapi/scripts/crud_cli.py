"""
Script CRUD con argumentos desde la línea de comandos.

CÓMO SE LLAMA:
    python djangoapi/manage.py runscript crud_cli --script-args <capa> <operacion> [param=valor ...]

ARGUMENTOS:
    capa        : zona | canal | estacion
    operacion   : insert | update | delete | select

EJEMPLOS:

  -- Listar todas las zonas
    python djangoapi/manage.py runscript crud_cli --script-args zona select

  -- Listar una zona por id
    python djangoapi/manage.py runscript crud_cli --script-args zona select id=1

  -- Insertar una zona
    python manage.py runscript crud_cli --script-args zona insert \\
        nombre_area="Reserva Norte" \\
        categoria_proteccion="Parque Nacional" \\
        fecha_declaracion=2010-06-15 \\
        geom="POLYGON((-2.60 39.40,-2.40 39.40,-2.40 39.60,-2.60 39.60,-2.60 39.40))"

  -- Insertar una linea
    python manage.py runscript crud_cli --script-args canal insert codigo_inventario="RN-3742" material_construccion="Concreto"  capacidad_caudal=135 longitud_km = 400 ultima_mantenimiento = 2024-02-01 geom="LINESTRING(-3.7038 40.4168, 2.1734 41.3851)"

  -- Actualizar una zona
    python djangoapi/manage.py runscript crud_cli --script-args zona update \\
        id=1 nombre_area="Nombre actualizado"

  -- Eliminar una zona
    python djangoapi/manage.py runscript crud_cli --script-args zona delete id=1

  -- Insertar una estación (el punto debe estar dentro de una zona existente)
    python djangoapi/manage.py runscript crud_cli --script-args estacion insert \\
        nombre="Estacion Alpha" tipo_sensor=Temperatura \\
        fecha_instalacion=2021-05-10 altitud_msnm=320.5 \\
        geom="POINT(-2.50 39.50)"
"""

import sys
from scripts.crud_zonas_conservacion import ZonaConservacionCRUD
from scripts.crud_red_canales import RedCanalCRUD
from scripts.crud_estaciones_monitoreo import EstacionMonitoreoCRUD


# ------------------------------------------------------------------ #
#  Mapeo de capas disponibles                                         #
# ------------------------------------------------------------------ #

CAPAS = {
    "zona":     ZonaConservacionCRUD,
    "canal":    RedCanalCRUD,
    "estacion": EstacionMonitoreoCRUD,
}

OPERACIONES = ("insert", "update", "delete", "select")


# ------------------------------------------------------------------ #
#  Parseo de argumentos  key=value → dict                            #
# ------------------------------------------------------------------ #

def _parsear_params(args: tuple) -> dict:
    """
    Convierte una secuencia de strings con formato 'clave=valor'
    en un diccionario de Python.

    Ejemplo:
        ("id=5", "nombre=Zona Norte")  →  {"id": 5, "nombre": "Zona Norte"}

    Conversiones automáticas de tipo:
        - Números enteros   → int
        - Números decimales → float
        - "true"/"false"    → bool
        - Todo lo demás     → str
    """
    params = {}
    for token in args:
        if "=" not in token:
            print(f"  [!] Argumento ignorado (formato incorrecto, debe ser clave=valor): '{token}'")
            continue

        clave, valor = token.split("=", 1)
        clave = clave.strip()
        valor = valor.strip()

        # Conversión automática de tipo
        if valor.lower() == "true":
            valor = True
        elif valor.lower() == "false":
            valor = False
        else:
            try:
                valor = int(valor)
            except ValueError:
                try:
                    valor = float(valor)
                except ValueError:
                    pass  # se queda como str

        params[clave] = valor

    return params


# ------------------------------------------------------------------ #
#  Impresión del resultado                                            #
# ------------------------------------------------------------------ #

def _imprimir(resultado: dict):
    estado = "OK" if resultado["ok"] else "ERROR / RECHAZADO"
    print(f"\n  Estado  : {estado}")
    print(f"  Mensaje : {resultado['message']}")
    if resultado.get("data"):
        print(f"  Data    :")
        for fila in resultado["data"]:
            print(f"    {fila}")
    print()


def _uso():
    print(__doc__)


# ------------------------------------------------------------------ #
#  Punto de entrada requerido por runscript                           #
# ------------------------------------------------------------------ #

def run(*args):
    """
    run() recibe como *args todo lo que el usuario pasa después de
    --script-args en la línea de comandos.

    Estructura esperada:
        args[0]  → nombre de la capa  (zona | canal | estacion)
        args[1]  → operación          (insert | update | delete | select)
        args[2+] → parámetros         clave=valor ...
    """

    # ── Validar que se recibieron al menos 2 argumentos ──────────── #
    if len(args) < 2:
        print("\n  [ERROR] Debes indicar al menos <capa> y <operacion>.")
        _uso()
        sys.exit(1)

    capa_nombre = args[0].lower()
    operacion   = args[1].lower()
    params      = _parsear_params(args[2:])

    # ── Validar capa ─────────────────────────────────────────────── #
    if capa_nombre not in CAPAS:
        print(f"\n  [ERROR] Capa desconocida: '{capa_nombre}'")
        print(f"  Capas disponibles: {', '.join(CAPAS.keys())}")
        sys.exit(1)

    # ── Validar operación ─────────────────────────────────────────── #
    if operacion not in OPERACIONES:
        print(f"\n  [ERROR] Operación desconocida: '{operacion}'")
        print(f"  Operaciones disponibles: {', '.join(OPERACIONES)}")
        sys.exit(1)

    # ── Instanciar el CRUD correspondiente ───────────────────────── #
    crud = CAPAS[capa_nombre]()

    print(f"\n  Capa      : {capa_nombre}")
    print(f"  Operación : {operacion}")
    print(f"  Parámetros: {params}")

    # ── Ejecutar la operación ─────────────────────────────────────── #
    if operacion == "insert":
        resultado = crud.insert(params)

    elif operacion == "update":
        resultado = crud.update(params)

    elif operacion == "delete":
        resultado = crud.delete(params)

    elif operacion == "select":
        resultado = crud.selectAsDicts(params if params else None)

    _imprimir(resultado)
