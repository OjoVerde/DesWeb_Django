# =============================================================================
# test_estaciones_monitoreo.py
#
# Archivo de pruebas para la clase EstacionesMonitoreo (geometría: Point).
#
# Regla espacial clave de este módulo:
#   Un punto (estación) SOLO puede insertarse o actualizarse si cae
#   estrictamente DENTRO de algún polígono de la tabla zonas_conservacion
#   (validado con ST_Within). Si el punto está fuera, la operación se rechaza.
#
# Por eso este test:
#   1. Primero inserta zonas de conservación de apoyo.
#   2. Ejecuta las pruebas de estaciones.
#   3. Al final limpia estaciones Y zonas, dejando la BD vacía.
#
# ¿Qué encontrarás aquí?
#   - Pruebas EXITOSAS: puntos válidos dentro de zonas.
#   - Pruebas RECHAZADAS: puntos fuera de zona, geometrías inválidas.
#   - Pruebas ERRÓNEAS: campos ausentes, tipos incorrectos, IDs inexistentes.
#
# Cómo ejecutarlo (dentro del contenedor Django):
#   python /workspace/psycopg/test_estaciones_monitoreo.py
# =============================================================================

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from estaciones_monitoreo.estaciones_monitoreo_OOP import EstacionesMonitoreo
from zonas_conservacion.zonas_conservacion_OOP import ZonasConservacion

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

    e  = EstacionesMonitoreo()
    z  = ZonasConservacion()

    ids_estaciones = []   # IDs de estaciones insertadas → para limpiar al final
    ids_zonas      = []   # IDs de zonas de apoyo       → para limpiar al final

    print("\n" + "=" * 60)
    print("  TEST: ESTACIONES DE MONITOREO")
    print("=" * 60)

    # ==========================================================================
    # PREPARACIÓN — Insertar zonas de conservación de apoyo
    #
    # Las estaciones solo pueden existir DENTRO de una zona. Por tanto,
    # necesitamos al menos una zona antes de poder insertar estaciones.
    # ==========================================================================
    print("\n>>> PREPARACIÓN: Insertando zonas de conservación de apoyo")

    # Zona A: rectángulo en la zona centro-norte de la cuadrícula de prueba.
    # Las estaciones válidas de este test caerán dentro de esta zona.
    rz1 = z.insert({
        'nombre_area'          : '[TEST] Zona Apoyo A',
        'categoria_proteccion' : 'Parque Natural',
        'entidad_responsable'  : 'Setup de pruebas',
        'area_hectareas'       : 2000.00,
        'fecha_declaracion'    : '2000-01-01',
        'geom': 'POLYGON((-4.00 41.00, -3.50 41.00, -3.50 41.30, -4.00 41.30, -4.00 41.00))'
    })
    mostrar("INSERT zona apoyo A (polígono grande norte)", rz1)
    if rz1["ok"]:
        ids_zonas.append(rz1["data"][0]["id"])

    # Zona B: rectángulo en el sur, completamente separado de la zona A.
    rz2 = z.insert({
        'nombre_area'          : '[TEST] Zona Apoyo B',
        'categoria_proteccion' : 'Reserva Natural',
        'entidad_responsable'  : 'Setup de pruebas',
        'area_hectareas'       : 1500.00,
        'fecha_declaracion'    : '2001-06-15',
        'geom': 'POLYGON((-3.00 40.00, -2.50 40.00, -2.50 40.30, -3.00 40.30, -3.00 40.00))'
    })
    mostrar("INSERT zona apoyo B (polígono pequeño sur)", rz2)
    if rz2["ok"]:
        ids_zonas.append(rz2["data"][0]["id"])

    # Verificamos que las zonas se crearon; si no, no tiene sentido continuar.
    if not ids_zonas:
        print("\n  ⚠ No se pudieron crear las zonas de apoyo. Abortando test.")
        e.disconnect()
        z.disconnect()
        return

    # ==========================================================================
    # SECCIÓN 1 — INSERCIONES EXITOSAS
    # Puntos que caen estrictamente dentro de una zona de conservación.
    # ==========================================================================
    print("\n>>> SECCIÓN 1: Inserciones exitosas")

    # Estación 1: centro geográfico aproximado de la zona A.
    # POINT(-3.75 41.15) está claramente dentro del polígono de la zona A.
    r1 = e.insert({
        'nombre'            : 'Estacion Alpha',
        'tipo_sensor'       : 'Temperatura',
        'fecha_instalacion' : '2021-03-10',
        'estado_operativo'  : True,
        'altitud_msnm'      : 950.00,
        'geom'              : 'POINT(-3.75 41.15)'
    })
    mostrar("INSERT estación 1 — dentro de zona A", r1)
    if r1["ok"]:
        ids_estaciones.append(r1["data"][0]["id"])

    # Estación 2: otro punto dentro de la zona A, pero en esquina diferente.
    r2 = e.insert({
        'nombre'            : 'Estacion Beta',
        'tipo_sensor'       : 'Humedad',
        'fecha_instalacion' : '2022-07-20',
        'estado_operativo'  : True,
        'altitud_msnm'      : 1100.00,
        'geom'              : 'POINT(-3.60 41.20)'
    })
    mostrar("INSERT estación 2 — dentro de zona A", r2)
    if r2["ok"]:
        ids_estaciones.append(r2["data"][0]["id"])

    # Estación 3: punto dentro de la zona B (diferente zona de apoyo).
    r3 = e.insert({
        'nombre'            : 'Estacion Gamma',
        'tipo_sensor'       : 'Precipitacion',
        'fecha_instalacion' : '2023-11-05',
        'estado_operativo'  : False,
        'altitud_msnm'      : 320.50,
        'geom'              : 'POINT(-2.75 40.15)'
    })
    mostrar("INSERT estación 3 — dentro de zona B", r3)
    if r3["ok"]:
        ids_estaciones.append(r3["data"][0]["id"])

    # ==========================================================================
    # SECCIÓN 2 — INSERCIONES RECHAZADAS (reglas espaciales)
    # ==========================================================================
    print("\n>>> SECCIÓN 2: Inserciones rechazadas por reglas espaciales")

    # Punto en el Océano Atlántico: fuera de cualquier zona de conservación.
    r_rej1 = e.insert({
        'nombre'            : 'Estacion Oceano',
        'tipo_sensor'       : 'Temperatura',
        'fecha_instalacion' : '2024-01-01',
        'estado_operativo'  : True,
        'altitud_msnm'      : 0.00,
        'geom'              : 'POINT(-10.00 36.00)'
    })
    mostrar("INSERT rechazado — punto en el océano (fuera de zona)", r_rej1)

    # Punto en el límite exterior de la zona A (exactamente en el borde).
    # ST_Within es ESTRICTO: el borde NO cuenta como "dentro".
    r_rej2 = e.insert({
        'nombre'            : 'Estacion Borde',
        'tipo_sensor'       : 'Viento',
        'fecha_instalacion' : '2024-02-14',
        'estado_operativo'  : True,
        'altitud_msnm'      : 900.00,
        'geom'              : 'POINT(-4.00 41.15)'   # x=-4.00 es el borde oeste de zona A
    })
    mostrar("INSERT rechazado — punto exactamente en el borde de zona A", r_rej2)

    # Punto cerca de la zona A pero ligeramente fuera.
    r_rej3 = e.insert({
        'nombre'            : 'Estacion Casi Dentro',
        'tipo_sensor'       : 'CO2',
        'fecha_instalacion' : '2024-03-01',
        'estado_operativo'  : True,
        'altitud_msnm'      : 870.00,
        'geom'              : 'POINT(-4.01 41.15)'   # 0.01° fuera del borde oeste
    })
    mostrar("INSERT rechazado — punto 0.01° fuera de zona A", r_rej3)

    # Intento con WKT de tipo LINESTRING en lugar de POINT.
    r_rej4 = e.insert({
        'nombre'            : 'Estacion WKT Erroneo',
        'tipo_sensor'       : 'Temperatura',
        'fecha_instalacion' : '2024-04-01',
        'estado_operativo'  : True,
        'altitud_msnm'      : 500.00,
        'geom'              : 'LINESTRING(-3.75 41.10, -3.70 41.20)'
    })
    mostrar("INSERT rechazado — WKT es LINESTRING en columna POINT", r_rej4)

    # ==========================================================================
    # SECCIÓN 3 — INSERCIONES ERRÓNEAS (datos mal formados)
    # ==========================================================================
    print("\n>>> SECCIÓN 3: Inserciones erróneas (datos inválidos)")

    # Falta el campo 'geom'.
    r_err1 = e.insert({
        'nombre'           : 'Estacion Sin Geom',
        'tipo_sensor'      : 'Presion',
        'altitud_msnm'     : 600.00
        # 'geom' ausente → KeyError capturado internamente
    })
    mostrar("INSERT erróneo — falta el campo 'geom'", r_err1)

    # Fecha de instalación con un texto que PostgreSQL no puede interpretar.
    # Nota: PostgreSQL acepta formatos como DD/MM/YYYY, por eso usamos un
    # valor completamente imposible para garantizar el error de tipo.
    r_err2 = e.insert({
        'nombre'            : 'Estacion Fecha Rota',
        'tipo_sensor'       : 'Temperatura',
        'fecha_instalacion' : 'not-a-date',   # texto sin ningún formato de fecha reconocible
        'estado_operativo'  : True,
        'altitud_msnm'      : 750.00,
        'geom'              : 'POINT(-3.75 41.15)'
    })
    mostrar("INSERT erróneo — formato de fecha inválido", r_err2)
    if r_err2["ok"]:   # salvaguarda: si inesperadamente pasa, lo rastreamos para limpieza
        ids_estaciones.append(r_err2["data"][0]["id"])

    # estado_operativo con texto en lugar de booleano.
    r_err3 = e.insert({
        'nombre'            : 'Estacion Bool Roto',
        'tipo_sensor'       : 'Humedad',
        'fecha_instalacion' : '2024-05-01',
        'estado_operativo'  : 'si',    # debería ser True/False
        'altitud_msnm'      : 820.00,
        'geom'              : 'POINT(-3.75 41.15)'
    })
    mostrar("INSERT erróneo — estado_operativo no es booleano", r_err3)

    # ==========================================================================
    # SECCIÓN 4 — ACTUALIZACIONES EXITOSAS
    # ==========================================================================
    print("\n>>> SECCIÓN 4: Actualizaciones exitosas")

    if ids_estaciones:
        id1 = ids_estaciones[0]

        # Cambiar nombre, tipo de sensor y altitud sin tocar la geometría.
        r_upd1 = e.update({
            'id'               : id1,
            'nombre'           : 'Estacion Alpha (Renovada)',
            'tipo_sensor'      : 'Temperatura + Humedad',
            'altitud_msnm'     : 980.00,
            'estado_operativo' : True
        })
        mostrar(f"UPDATE atributos — id={id1}", r_upd1)

        # Mover la estación a otro punto que también está dentro de zona A.
        r_upd2 = e.update({
            'id'  : id1,
            'geom': 'POINT(-3.80 41.05)'
        })
        mostrar(f"UPDATE geometría válida (sigue en zona A) — id={id1}", r_upd2)

    if len(ids_estaciones) >= 2:
        id2 = ids_estaciones[1]

        # Desactivar operativamente la estación 2.
        r_upd3 = e.update({
            'id'               : id2,
            'estado_operativo' : False,
            'nombre'           : 'Estacion Beta (Inactiva)'
        })
        mostrar(f"UPDATE estado_operativo=False — id={id2}", r_upd3)

    # ==========================================================================
    # SECCIÓN 5 — ACTUALIZACIONES RECHAZADAS
    # ==========================================================================
    print("\n>>> SECCIÓN 5: Actualizaciones rechazadas")

    if ids_estaciones:
        id1 = ids_estaciones[0]

        # Intentar mover la estación fuera de cualquier zona de conservación.
        r_upd_rej1 = e.update({
            'id'  : id1,
            'geom': 'POINT(0.00 0.00)'   # coordenadas en el Golfo de Guinea
        })
        mostrar(f"UPDATE rechazado — mover fuera de zona — id={id1}", r_upd_rej1)

        # Intentar mover la estación al borde exacto de la zona A (ST_Within estricto).
        r_upd_rej2 = e.update({
            'id'  : id1,
            'geom': 'POINT(-3.50 41.15)'   # x=-3.50 es el borde este de zona A
        })
        mostrar(f"UPDATE rechazado — mover al borde de zona A — id={id1}", r_upd_rej2)

    # Update sin proporcionar ningún campo para modificar.
    if ids_estaciones:
        r_upd_rej3 = e.update({'id': ids_estaciones[0]})
        mostrar("UPDATE rechazado — ningún campo enviado", r_upd_rej3)

    # Update sobre un ID inexistente.
    r_upd_rej4 = e.update({
        'id'          : 999999,
        'altitud_msnm': 1000.00
    })
    mostrar("UPDATE rechazado — id=999999 no existe", r_upd_rej4)

    # ==========================================================================
    # SECCIÓN 6 — CONSULTAS (SELECT)
    # ==========================================================================
    print("\n>>> SECCIÓN 6: Consultas SELECT")

    # Todos los registros como lista de tuplas.
    r_sel1 = e.selectAsTuples({})
    mostrar("SELECT todos (tuples)", r_sel1)

    # Todos los registros como lista de diccionarios.
    r_sel2 = e.selectAsDicts({})
    mostrar("SELECT todos (dicts)", r_sel2)

    # Filtrar por un ID concreto.
    if ids_estaciones:
        r_sel3 = e.selectAsDicts({'id': ids_estaciones[0]})
        mostrar(f"SELECT por id={ids_estaciones[0]} (dicts)", r_sel3)

    # Filtrar por ID inexistente → lista vacía, no error.
    r_sel4 = e.selectAsTuples({'id': 999999})
    mostrar("SELECT id=999999 — lista vacía esperada", r_sel4)

    # ==========================================================================
    # SECCIÓN 7 — ELIMINACIONES Y LIMPIEZA
    # Orden correcto: primero estaciones, luego zonas de apoyo.
    # Si intentáramos borrar las zonas primero, las estaciones quedarían
    # huérfanas y sin zona contenedora (aunque PostgreSQL no lo impide aquí,
    # es buena práctica respetar el orden lógico de dependencia).
    # ==========================================================================
    print("\n>>> SECCIÓN 7: Eliminaciones y limpieza")

    # Borrar un ID de estación inexistente.
    r_del_err = e.delete({'id': 999999})
    mostrar("DELETE estación id=999999 — no existe", r_del_err)

    # Borrar todas las estaciones insertadas en este test.
    print("\n  -- Limpieza estaciones --")
    for rid in ids_estaciones:
        r_del = e.delete({'id': rid})
        mostrar(f"DELETE estación id={rid}", r_del)

    # Verificar que la tabla de estaciones quedó vacía.
    r_check_est = e.selectAsTuples({})
    mostrar("SELECT estaciones tras limpieza — debe estar vacía", r_check_est)

    # Borrar todas las zonas de apoyo.
    print("\n  -- Limpieza zonas de conservación de apoyo --")
    for rid in ids_zonas:
        r_del_z = z.delete({'id': rid})
        mostrar(f"DELETE zona id={rid}", r_del_z)

    # Verificar que la tabla de zonas quedó vacía.
    r_check_zon = z.selectAsTuples({})
    mostrar("SELECT zonas tras limpieza — debe estar vacía", r_check_zon)

    e.disconnect()
    z.disconnect()

    print("\n" + "=" * 60)
    print("  FIN DE PRUEBAS — EstacionesMonitoreo")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
