"""
Script de prueba para las clases CRUD de app_conservacion.

Ejecución (dentro del contenedor Django):
    python djangoapi/manage.py runscript test_conservacion

La función run() es el punto de entrada requerido por django-extensions runscript.
Al finalizar, la base de datos queda en el mismo estado que al inicio (limpia).
"""

from scripts.crud_zonas_conservacion import ZonaConservacionCRUD
from scripts.crud_red_canales import RedCanalCRUD
from scripts.crud_estaciones_monitoreo import EstacionMonitoreoCRUD


# ------------------------------------------------------------------ #
#  Utilidad de impresión                                              #
# ------------------------------------------------------------------ #

def _print_resultado(titulo: str, resultado: dict):
    """Imprime el resultado de una operación de forma legible."""
    estado = "✔ OK " if resultado["ok"] else "✘ RECHAZADO/ERROR"
    print(f"\n  [{estado}] {titulo}")
    print(f"         mensaje : {resultado['message']}")
    if resultado.get("data"):
        print(f"         data    : {resultado['data']}")


def _seccion(titulo: str):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}")


# ------------------------------------------------------------------ #
#  Punto de entrada requerido por runscript                           #
# ------------------------------------------------------------------ #

def run():
    zona_crud    = ZonaConservacionCRUD()
    canal_crud   = RedCanalCRUD()
    estacion_crud = EstacionMonitoreoCRUD()

    ids_zonas    = []
    ids_canales  = []
    ids_estaciones = []

    # ============================================================ #
    #  1. ZONAS DE CONSERVACIÓN                                    #
    # ============================================================ #
    _seccion("1. ZONAS DE CONSERVACIÓN — INSERT exitoso")

    r = zona_crud.insert({
        "nombre_area": "Zona Norte A",
        "categoria_proteccion": "Reserva Natural",
        "entidad_responsable": "Ministerio de Medio Ambiente",
        "area_hectareas": 1500.50,
        "fecha_declaracion": "2010-06-15",
        "geom": "POLYGON((-2.60 39.40, -2.40 39.40, -2.40 39.60, -2.60 39.60, -2.60 39.40))"
    })
    _print_resultado("INSERT Zona Norte A", r)
    if r["ok"]:
        ids_zonas.append(r["data"][0]["id"])

    r = zona_crud.insert({
        "nombre_area": "Zona Sur B",
        "categoria_proteccion": "Parque Nacional",
        "entidad_responsable": "Gobierno Regional",
        "area_hectareas": 800.00,
        "fecha_declaracion": "2015-03-22",
        "geom": "POLYGON((-2.60 39.00, -2.40 39.00, -2.40 39.20, -2.60 39.20, -2.60 39.00))"
    })
    _print_resultado("INSERT Zona Sur B", r)
    if r["ok"]:
        ids_zonas.append(r["data"][0]["id"])

    # ------------------------------------------------------------ #
    _seccion("1b. ZONAS DE CONSERVACIÓN — INSERT rechazado (intersección)")

    r = zona_crud.insert({
        "nombre_area": "Zona Solapada (debe fallar)",
        "geom": "POLYGON((-2.55 39.35, -2.35 39.35, -2.35 39.55, -2.55 39.55, -2.55 39.35))"
    })
    _print_resultado("INSERT zona que solapa con Zona Norte A", r)

    r = zona_crud.insert({
        "nombre_area": "Sin geometría (debe fallar)",
    })
    _print_resultado("INSERT sin campo 'geom'", r)

    r = zona_crud.insert({
        "nombre_area": "Geometría inválida (debe fallar)",
        "geom": "POLYGON((0 0, 1 1, 1 0, 0 1, 0 0))"  # auto-intersección
    })
    _print_resultado("INSERT con geometría con auto-intersección", r)

    # ------------------------------------------------------------ #
    _seccion("1c. ZONAS DE CONSERVACIÓN — SELECT")

    r = zona_crud.selectAsDicts()
    _print_resultado(f"selectAsDicts (todos)", r)

    r = zona_crud.selectAsTuples({"id": ids_zonas[0]})
    _print_resultado(f"selectAsTuples (id={ids_zonas[0]})", r)

    # ------------------------------------------------------------ #
    _seccion("1d. ZONAS DE CONSERVACIÓN — UPDATE")

    r = zona_crud.update({
        "id": ids_zonas[0],
        "entidad_responsable": "Ministerio ACTUALIZADO",
        "area_hectareas": 1600.00
    })
    _print_resultado(f"UPDATE campos alfanuméricos id={ids_zonas[0]}", r)

    r = zona_crud.update({
        "id": 999999,
        "nombre_area": "No existe (debe fallar)"
    })
    _print_resultado("UPDATE id inexistente", r)

    # ============================================================ #
    #  2. RED DE CANALES                                           #
    # ============================================================ #
    _seccion("2. RED DE CANALES — INSERT exitoso")

    r = canal_crud.insert({
        "codigo_inventario": "CAN-001",
        "material_construccion": "Hormigón",
        "capacidad_caudal": 12.500,
        "ultimo_mantenimiento": "2023-09-01T08:00:00",
        "geom": "LINESTRING(-2.58 39.50, -2.45 39.50)"
    })
    _print_resultado("INSERT Canal CAN-001 (horizontal norte)", r)
    if r["ok"]:
        ids_canales.append(r["data"][0]["id"])

    r = canal_crud.insert({
        "codigo_inventario": "CAN-002",
        "material_construccion": "PVC",
        "capacidad_caudal": 5.200,
        "ultimo_mantenimiento": "2024-01-15T10:30:00",
        "geom": "LINESTRING(-2.58 39.10, -2.45 39.10)"
    })
    _print_resultado("INSERT Canal CAN-002 (horizontal sur)", r)
    if r["ok"]:
        ids_canales.append(r["data"][0]["id"])

    # ------------------------------------------------------------ #
    _seccion("2b. RED DE CANALES — INSERT rechazado (intersección)")

    r = canal_crud.insert({
        "codigo_inventario": "CAN-CROSS",
        "geom": "LINESTRING(-2.50 39.55, -2.50 39.45)"  # cruza CAN-001
    })
    _print_resultado("INSERT canal que cruza CAN-001 (debe fallar)", r)

    r = canal_crud.insert({
        "codigo_inventario": "CAN-001",  # duplicado
        "geom": "LINESTRING(-2.30 39.80, -2.10 39.80)"
    })
    _print_resultado("INSERT codigo_inventario duplicado (debe fallar)", r)

    # ------------------------------------------------------------ #
    _seccion("2c. RED DE CANALES — SELECT y UPDATE")

    r = canal_crud.selectAsDicts()
    _print_resultado("selectAsDicts (todos)", r)

    r = canal_crud.update({
        "id": ids_canales[0],
        "material_construccion": "Acero ACTUALIZADO",
    })
    _print_resultado(f"UPDATE campos alfanuméricos canal id={ids_canales[0]}", r)

    # ============================================================ #
    #  3. ESTACIONES DE MONITOREO                                  #
    # ============================================================ #
    _seccion("3. ESTACIONES DE MONITOREO — INSERT exitoso (punto dentro de zona)")

    r = estacion_crud.insert({
        "nombre": "Estacion Alpha",
        "tipo_sensor": "Temperatura",
        "fecha_instalacion": "2021-05-10",
        "estado_operativo": True,
        "altitud_msnm": 320.50,
        "geom": "POINT(-2.50 39.50)"  # dentro de Zona Norte A
    })
    _print_resultado("INSERT Estacion Alpha (dentro de Zona Norte A)", r)
    if r["ok"]:
        ids_estaciones.append(r["data"][0]["id"])

    r = estacion_crud.insert({
        "nombre": "Estacion Beta",
        "tipo_sensor": "Humedad",
        "fecha_instalacion": "2022-07-20",
        "estado_operativo": True,
        "altitud_msnm": 410.00,
        "geom": "POINT(-2.50 39.10)"  # dentro de Zona Sur B
    })
    _print_resultado("INSERT Estacion Beta (dentro de Zona Sur B)", r)
    if r["ok"]:
        ids_estaciones.append(r["data"][0]["id"])

    # ------------------------------------------------------------ #
    _seccion("3b. ESTACIONES DE MONITOREO — INSERT rechazado")

    r = estacion_crud.insert({
        "nombre": "Fuera de zona (debe fallar)",
        "geom": "POINT(-3.00 40.00)"  # fuera de cualquier zona
    })
    _print_resultado("INSERT punto fuera de toda zona (ST_Within falla)", r)

    r = estacion_crud.insert({
        "nombre": "Sin geometría (debe fallar)",
    })
    _print_resultado("INSERT sin campo 'geom'", r)

    r = estacion_crud.insert({
        "nombre": "Sin nombre (debe fallar)",
        "geom": "POINT(-2.50 39.50)"
    })
    _print_resultado("INSERT sin campo 'nombre'", r)

    # ------------------------------------------------------------ #
    _seccion("3c. ESTACIONES DE MONITOREO — SELECT y UPDATE")

    r = estacion_crud.selectAsDicts()
    _print_resultado("selectAsDicts (todas)", r)

    r = estacion_crud.selectAsTuples({"id": ids_estaciones[0]})
    _print_resultado(f"selectAsTuples (id={ids_estaciones[0]})", r)

    r = estacion_crud.update({
        "id": ids_estaciones[0],
        "tipo_sensor": "Temperatura + CO2",
        "altitud_msnm": 350.00
    })
    _print_resultado(f"UPDATE campos alfanuméricos estacion id={ids_estaciones[0]}", r)

    r = estacion_crud.update({
        "id": ids_estaciones[0],
        "geom": "POINT(-3.00 40.00)"  # mover fuera de zona
    })
    _print_resultado("UPDATE mover punto fuera de zona (debe fallar)", r)

    # ============================================================ #
    #  4. LIMPIEZA — se elimina todo en orden inverso              #
    # ============================================================ #
    _seccion("4. LIMPIEZA FINAL (deja la DB en estado inicial)")

    for eid in ids_estaciones:
        r = estacion_crud.delete({"id": eid})
        _print_resultado(f"DELETE estacion id={eid}", r)

    for cid in ids_canales:
        r = canal_crud.delete({"id": cid})
        _print_resultado(f"DELETE canal id={cid}", r)

    for zid in ids_zonas:
        r = zona_crud.delete({"id": zid})
        _print_resultado(f"DELETE zona id={zid}", r)

    # Verificación final
    _seccion("5. VERIFICACIÓN FINAL — todas las tablas deben estar vacías")

    r = zona_crud.selectAsDicts()
    _print_resultado(f"Zonas restantes: {len(r.get('data') or [])}", r)

    r = canal_crud.selectAsDicts()
    _print_resultado(f"Canales restantes: {len(r.get('data') or [])}", r)

    r = estacion_crud.selectAsDicts()
    _print_resultado(f"Estaciones restantes: {len(r.get('data') or [])}", r)

    print("\n" + "="*60)
    print("  Script test_conservacion finalizado.")
    print("="*60 + "\n")
