# =============================================================================
# test_red_canales.py
#
# Archivo de pruebas para la clase RedCanales (geometría: LineString).
#
# ¿Qué encontrarás aquí?
#   - Pruebas EXITOSAS: inserciones, actualizaciones y consultas correctas.
#   - Pruebas RECHAZADAS: líneas que intersectan con otras ya existentes,
#     geometrías inválidas, etc.
#   - Pruebas ERRÓNEAS: campos ausentes, tipos incorrectos, IDs inexistentes.
#
# Al final, el script elimina TODOS los registros que insertó, dejando la base
# de datos exactamente igual que antes de ejecutarse.
#
# Cómo ejecutarlo (dentro del contenedor Django):
#   python /workspace/psycopg/test_red_canales.py
# =============================================================================

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from red_canales.red_canales_OOP import RedCanales

# ------------------------------------------------------------------------------
# Utilidad de presentación
# ------------------------------------------------------------------------------
def mostrar(etiqueta, resultado):
    ok_str = "✔ OK" if resultado["ok"] else "✘ FALLO / RECHAZADO"
    print(f"\n  {'─'*56}")
    print(f"  {ok_str}  »  {etiqueta}")
    print(f"  {'─'*56}")
    print(f"  mensaje : {resultado['message']}")
    print(f"  data    : {resultado['data']}")


# ==============================================================================
# BLOQUE PRINCIPAL
# ==============================================================================
def main():

    c = RedCanales()
    ids_insertados = []

    print("\n" + "=" * 60)
    print("  TEST: RED DE CANALES")
    print("=" * 60)

    # ==========================================================================
    # SECCIÓN 1 — INSERCIONES EXITOSAS
    # Líneas que no se cruzan entre sí.
    # ==========================================================================
    print("\n>>> SECCIÓN 1: Inserciones exitosas")

    # Canal 1: tramo horizontal en la zona norte.
    # No existe ningún otro canal en la BD → debe insertarse sin problemas.
    r1 = c.insert({
        'codigo_inventario'    : 'CAN-N01',
        'material_construccion': 'Hormigon',
        'capacidad_caudal'     : 12.500,
        'ultimo_mantenimiento' : '2023-04-10 08:00:00',
        'geom': 'LINESTRING(-4.00 41.05, -3.80 41.05, -3.60 41.05)'
    })
    mostrar("INSERT canal 1 — tramo horizontal norte", r1)
    if r1["ok"]:
        ids_insertados.append(r1["data"][0]["id"])

    # Canal 2: tramo vertical separado del anterior, sin intersección.
    r2 = c.insert({
        'codigo_inventario'    : 'CAN-V01',
        'material_construccion': 'PVC',
        'capacidad_caudal'     : 5.000,
        'ultimo_mantenimiento' : '2024-01-22 10:30:00',
        'geom': 'LINESTRING(-3.10 40.60, -3.10 40.75)'
    })
    mostrar("INSERT canal 2 — tramo vertical este", r2)
    if r2["ok"]:
        ids_insertados.append(r2["data"][0]["id"])

    # Canal 3: tramo diagonal en una zona completamente diferente.
    r3 = c.insert({
        'codigo_inventario'    : 'CAN-D01',
        'material_construccion': 'Acero',
        'capacidad_caudal'     : 28.750,
        'ultimo_mantenimiento' : '2022-09-15 07:00:00',
        'geom': 'LINESTRING(-2.50 39.50, -2.30 39.70, -2.10 39.90)'
    })
    mostrar("INSERT canal 3 — tramo diagonal sur", r3)
    if r3["ok"]:
        ids_insertados.append(r3["data"][0]["id"])

    # ==========================================================================
    # SECCIÓN 2 — INSERCIONES RECHAZADAS (reglas espaciales)
    # ST_Intersects detecta cruces con canales ya existentes.
    # ==========================================================================
    print("\n>>> SECCIÓN 2: Inserciones rechazadas por reglas espaciales")

    # Intento de insertar una línea vertical que cruza el canal 1 (horizontal).
    # El cruce se produce en el punto (-3.80, 41.05).
    r_rej1 = c.insert({
        'codigo_inventario'    : 'CAN-CRUCE01',
        'material_construccion': 'Hierro',
        'capacidad_caudal'     : 7.000,
        'ultimo_mantenimiento' : '2024-02-01 09:00:00',
        'geom': 'LINESTRING(-3.80 41.00, -3.80 41.10)'
    })
    mostrar("INSERT rechazado — cruza perpendicularmente canal 1", r_rej1)

    # Intento de insertar una copia exacta del canal 2.
    r_rej2 = c.insert({
        'codigo_inventario'    : 'CAN-DUP01',
        'material_construccion': 'PVC',
        'capacidad_caudal'     : 5.000,
        'ultimo_mantenimiento' : '2024-01-22 10:30:00',
        'geom': 'LINESTRING(-3.10 40.60, -3.10 40.75)'
    })
    mostrar("INSERT rechazado — duplicado exacto del canal 2", r_rej2)

    # Intento con una geometría de línea inválida (un único punto no forma línea).
    # PostGIS lanzará un error al intentar parsear el WKT.
    r_rej3 = c.insert({
        'codigo_inventario'    : 'CAN-INVALIDO',
        'material_construccion': 'Madera',
        'capacidad_caudal'     : 1.000,
        'ultimo_mantenimiento' : '2024-03-01 00:00:00',
        'geom': 'LINESTRING(0.0 0.0)'  # línea degenerada: solo un punto
    })
    mostrar("INSERT rechazado — LineString degenerada (1 solo punto)", r_rej3)

    # ==========================================================================
    # SECCIÓN 3 — INSERCIONES ERRÓNEAS (datos mal formados)
    # ==========================================================================
    print("\n>>> SECCIÓN 3: Inserciones erróneas (datos inválidos)")

    # Falta el campo obligatorio 'geom'.
    r_err1 = c.insert({
        'codigo_inventario'    : 'CAN-SINGEOM',
        'material_construccion': 'Hormigon',
        'capacidad_caudal'     : 10.000
        # 'geom' ausente → KeyError capturado
    })
    mostrar("INSERT erróneo — falta el campo 'geom'", r_err1)

    # El WKT tiene tipo POLYGON en lugar de LINESTRING.
    r_err2 = c.insert({
        'codigo_inventario'    : 'CAN-WKTERR',
        'material_construccion': 'Hormigon',
        'capacidad_caudal'     : 9.000,
        'ultimo_mantenimiento' : '2024-04-01 00:00:00',
        'geom': 'POLYGON((-3.00 40.00, -2.80 40.00, -2.80 40.10, -3.00 40.10, -3.00 40.00))'
    })
    mostrar("INSERT erróneo — WKT es POLYGON en columna LINESTRING", r_err2)

    # Valor numérico inválido: texto en lugar de número para capacidad_caudal.
    r_err3 = c.insert({
        'codigo_inventario'    : 'CAN-NUMERR',
        'material_construccion': 'PVC',
        'capacidad_caudal'     : 'mucho',   # debería ser numérico
        'ultimo_mantenimiento' : '2024-05-01 00:00:00',
        'geom': 'LINESTRING(-1.00 38.00, -0.80 38.20)'
    })
    mostrar("INSERT erróneo — capacidad_caudal no es número", r_err3)

    # ==========================================================================
    # SECCIÓN 4 — ACTUALIZACIONES EXITOSAS
    # ==========================================================================
    print("\n>>> SECCIÓN 4: Actualizaciones exitosas")

    if ids_insertados:
        id1 = ids_insertados[0]

        # Actualizar solo atributos alfanuméricos del canal 1.
        r_upd1 = c.update({
            'id'                   : id1,
            'material_construccion': 'Hormigon Pretensado',
            'capacidad_caudal'     : 15.000,
        })
        mostrar(f"UPDATE atributos — id={id1}", r_upd1)

        # Mover el canal 1 a una posición que no interfiere con nadie.
        r_upd2 = c.update({
            'id'  : id1,
            'geom': 'LINESTRING(-5.00 42.00, -4.80 42.00, -4.60 42.00)'
        })
        mostrar(f"UPDATE geometría válida — id={id1}", r_upd2)

    # ==========================================================================
    # SECCIÓN 5 — ACTUALIZACIONES RECHAZADAS
    # ==========================================================================
    print("\n>>> SECCIÓN 5: Actualizaciones rechazadas")

    if len(ids_insertados) >= 2:
        id2 = ids_insertados[1]

        # Intentar mover el canal 2 a una posición que cruza el canal 3.
        r_upd_rej1 = c.update({
            'id'  : id2,
            'geom': 'LINESTRING(-2.40 39.40, -2.20 39.80)'
        })
        mostrar(f"UPDATE rechazado — nueva geom cruza canal 3", r_upd_rej1)

    # Actualizar un ID inexistente.
    r_upd_rej2 = c.update({
        'id'           : 999999,
    })
    mostrar("UPDATE rechazado — id=999999 no existe", r_upd_rej2)

    # Update sin ningún campo modificable.
    if ids_insertados:
        r_upd_rej3 = c.update({'id': ids_insertados[0]})
        mostrar("UPDATE rechazado — ningún campo enviado", r_upd_rej3)

    # ==========================================================================
    # SECCIÓN 6 — CONSULTAS (SELECT)
    # ==========================================================================
    print("\n>>> SECCIÓN 6: Consultas SELECT")

    r_sel1 = c.selectAsTuples({})
    mostrar("SELECT todos (tuples)", r_sel1)

    r_sel2 = c.selectAsDicts({})
    mostrar("SELECT todos (dicts)", r_sel2)

    if ids_insertados:
        r_sel3 = c.selectAsDicts({'id': ids_insertados[0]})
        mostrar(f"SELECT por id={ids_insertados[0]} (dicts)", r_sel3)

    # ID inexistente → lista vacía, no error.
    r_sel4 = c.selectAsTuples({'id': 999999})
    mostrar("SELECT id=999999 — lista vacía esperada", r_sel4)

    # ==========================================================================
    # SECCIÓN 7 — ELIMINACIONES Y LIMPIEZA
    # ==========================================================================
    print("\n>>> SECCIÓN 7: Eliminaciones")

    # Borrar un ID que no existe.
    r_del_err = c.delete({'id': 999999})
    mostrar("DELETE id=999999 — no existe", r_del_err)

    # Borrar todos los registros insertados en este test.
    print("\n  -- Limpieza: borrando registros insertados en este test --")
    for rid in ids_insertados:
        r_del = c.delete({'id': rid})
        mostrar(f"DELETE id={rid}", r_del)

    # Verificar estado final de la tabla.
    r_final = c.selectAsTuples({})
    mostrar("SELECT final — debe estar vacía", r_final)

    c.disconnect()

    print("\n" + "=" * 60)
    print("  FIN DE PRUEBAS — RedCanales")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
