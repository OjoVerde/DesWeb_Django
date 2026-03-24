# =============================================================================
# test_zonas_conservacion.py
#
# Archivo de pruebas para la clase ZonasConservacion (geometría: Polígono).
#
# ¿Qué encontrarás aquí?
#   - Pruebas EXITOSAS: operaciones que deben completarse sin errores.
#   - Pruebas RECHAZADAS: operaciones que el sistema debe bloquear por reglas
#     espaciales (intersección, geometría inválida, etc.).
#   - Pruebas ERRÓNEAS: llamadas con datos mal formados o campos que no existen.
#
# Al final, el script elimina TODOS los registros que insertó, dejando la base
# de datos exactamente igual que antes de ejecutarse.
#
# Cómo ejecutarlo (dentro del contenedor Django):
#   python /workspace/psycopg/test_zonas_conservacion.py
# =============================================================================

import sys
import os

# Añadimos la carpeta raíz del proyecto al path de Python para que pueda
# encontrar los módulos 'db', 'zonas_conservacion', etc.
sys.path.insert(0, os.path.dirname(__file__))

from zonas_conservacion.zonas_conservacion_OOP import ZonasConservacion

# ------------------------------------------------------------------------------
# Utilidad de presentación
# Imprime el resultado de cada prueba de forma clara y legible.
# ------------------------------------------------------------------------------
def mostrar(etiqueta, resultado):
    ok_str  = "✔ OK" if resultado["ok"] else "✘ FALLO / RECHAZADO"
    print(f"\n  {'─'*56}")
    print(f"  {ok_str}  »  {etiqueta}")
    print(f"  {'─'*56}")
    print(f"  mensaje : {resultado['message']}")
    print(f"  data    : {resultado['data']}")


# ==============================================================================
# BLOQUE PRINCIPAL
# ==============================================================================
def main():

    # Creamos una única instancia; esto abre la conexión a la base de datos.
    z = ZonasConservacion()

    # Lista donde guardaremos los IDs insertados para borrarlos al final.
    ids_insertados = []

    print("\n" + "=" * 60)
    print("  TEST: ZONAS DE CONSERVACIÓN")
    print("=" * 60)

    # ==========================================================================
    # SECCIÓN 1 — INSERCIONES EXITOSAS
    # Polígonos geográficamente válidos y sin solapamiento entre sí.
    # ==========================================================================
    print("\n>>> SECCIÓN 1: Inserciones exitosas")

    # Polígono 1: área pequeña en el noroeste de la cuadrícula de prueba.
    # Es válido y no toca ningún otro registro existente.
    r1 = z.insert({
        'nombre_area'          : 'Reserva Bosque Norte',
        'categoria_proteccion' : 'Reserva Natural',
        'entidad_responsable'  : 'Ministerio de Medio Ambiente',
        'area_hectareas'       : 1200.50,
        'fecha_declaracion'    : '2005-03-15',
        'geom': 'POLYGON((-4.00 41.00, -3.80 41.00, -3.80 41.10, -4.00 41.10, -4.00 41.00))'
    })
    mostrar("INSERT polígono 1 — Reserva Bosque Norte", r1)
    if r1["ok"]:
        ids_insertados.append(r1["data"][0]["id"])

    # Polígono 2: zona completamente separada del polígono anterior.
    r2 = z.insert({
        'nombre_area'          : 'Parque Humedal Sur',
        'categoria_proteccion' : 'Parque Natural',
        'entidad_responsable'  : 'Gobierno Regional',
        'area_hectareas'       : 3400.00,
        'fecha_declaracion'    : '2012-07-01',
        'geom': 'POLYGON((-3.50 40.60, -3.30 40.60, -3.30 40.75, -3.50 40.75, -3.50 40.60))'
    })
    mostrar("INSERT polígono 2 — Parque Humedal Sur", r2)
    if r2["ok"]:
        ids_insertados.append(r2["data"][0]["id"])

    # Polígono 3: zona adyacente pero sin solapamiento con las anteriores.
    r3 = z.insert({
        'nombre_area'          : 'Corredor Ecológico Este',
        'categoria_proteccion' : 'Corredor Biológico',
        'entidad_responsable'  : 'ONG Verde Vivo',
        'area_hectareas'       : 870.25,
        'fecha_declaracion'    : '2018-11-20',
        'geom': 'POLYGON((-3.20 40.60, -3.00 40.60, -3.00 40.75, -3.20 40.75, -3.20 40.60))'
    })
    mostrar("INSERT polígono 3 — Corredor Ecológico Este", r3)
    if r3["ok"]:
        ids_insertados.append(r3["data"][0]["id"])

    # ==========================================================================
    # SECCIÓN 2 — INSERCIONES RECHAZADAS (reglas espaciales)
    # El sistema debe bloquear estas operaciones y devolver ok=False.
    # ==========================================================================
    print("\n>>> SECCIÓN 2: Inserciones rechazadas por reglas espaciales")

    # Intento de insertar un polígono que se superpone con el polígono 1.
    # ST_Intersects detecta el solapamiento → rechazo.
    r_rej1 = z.insert({
        'nombre_area'          : 'Zona Solapada con Bosque Norte',
        'categoria_proteccion' : 'Reserva',
        'entidad_responsable'  : 'Entidad X',
        'area_hectareas'       : 500.00,
        'fecha_declaracion'    : '2020-01-01',
        'geom': 'POLYGON((-3.90 40.95, -3.70 40.95, -3.70 41.05, -3.90 41.05, -3.90 40.95))'
    })
    mostrar("INSERT rechazado — solapa con polígono 1", r_rej1)

    # Intento con una geometría espacialmente inválida.
    # Un polígono con los lados cruzados (lazo) no supera ST_IsValid.
    r_rej2 = z.insert({
        'nombre_area'          : 'Zona con geometría en lazo',
        'categoria_proteccion' : 'Reserva',
        'entidad_responsable'  : 'Entidad Y',
        'area_hectareas'       : 100.00,
        'fecha_declaracion'    : '2021-06-10',
        'geom': 'POLYGON((-2.00 39.00, -1.80 39.20, -1.80 39.00, -2.00 39.20, -2.00 39.00))'
    })
    mostrar("INSERT rechazado — geometría inválida (lazo)", r_rej2)

    # Intento de insertar un polígono que cubre exactamente el mismo área que
    # el polígono 2 (duplicado exacto).
    r_rej3 = z.insert({
        'nombre_area'          : 'Duplicado de Humedal Sur',
        'categoria_proteccion' : 'Parque Natural',
        'entidad_responsable'  : 'Gobierno Regional',
        'area_hectareas'       : 3400.00,
        'fecha_declaracion'    : '2012-07-01',
        'geom': 'POLYGON((-3.50 40.60, -3.30 40.60, -3.30 40.75, -3.50 40.75, -3.50 40.60))'
    })
    mostrar("INSERT rechazado — duplicado exacto del polígono 2", r_rej3)

    # ==========================================================================
    # SECCIÓN 3 — INSERCIONES ERRÓNEAS (datos mal formados)
    # Errores de tipo o campos obligatorios ausentes.
    # ==========================================================================
    print("\n>>> SECCIÓN 3: Inserciones erróneas (datos inválidos)")

    # Falta el campo 'geom'. La clase debe capturar el KeyError y devolver ok=False.
    r_err1 = z.insert({
        'nombre_area'       : 'Zona sin geometría',
        'area_hectareas'    : 200.00,
        'fecha_declaracion' : '2023-01-01'
        # 'geom' no está incluido → KeyError
    })
    mostrar("INSERT erróneo — falta el campo 'geom'", r_err1)

    # Valor de fecha con formato incorrecto (no es ISO 8601).
    r_err2 = z.insert({
        'nombre_area'          : 'Zona fecha inválida',
        'categoria_proteccion' : 'Reserva',
        'area_hectareas'       : 300.00,
        'fecha_declaracion'    : '20-enero-2022',  # formato inválido para PostgreSQL
        'geom': 'POLYGON((-1.00 38.00, -0.80 38.00, -0.80 38.10, -1.00 38.10, -1.00 38.00))'
    })
    mostrar("INSERT erróneo — formato de fecha inválido", r_err2)

    # WKT con tipo de geometría incorrecto (POINT en lugar de POLYGON).
    r_err3 = z.insert({
        'nombre_area'          : 'Zona con WKT erróneo',
        'categoria_proteccion' : 'Reserva',
        'area_hectareas'       : 150.00,
        'fecha_declaracion'    : '2022-05-05',
        'geom': 'POINT(-3.70 40.45)'  # tipo incorrecto para la columna POLYGON
    })
    mostrar("INSERT erróneo — WKT es POINT en columna POLYGON", r_err3)

    # ==========================================================================
    # SECCIÓN 4 — ACTUALIZACIONES EXITOSAS
    # Modificar campos alfanuméricos y geométricos de registros válidos.
    # ==========================================================================
    print("\n>>> SECCIÓN 4: Actualizaciones exitosas")

    if ids_insertados:
        id1 = ids_insertados[0]

        # Actualizar solo atributos alfanuméricos (sin tocar la geometría).
        r_upd1 = z.update({
            'id'                   : id1,
            'nombre_area'          : 'Reserva Bosque Norte (Ampliada)',
            'area_hectareas'       : 1500.00,
            'entidad_responsable'  : 'Ministerio Actualizado'
        })
        mostrar(f"UPDATE atributos — id={id1}", r_upd1)

        # Actualizar la geometría a un polígono que no solapa con ningún otro.
        r_upd2 = z.update({
            'id'  : id1,
            'geom': 'POLYGON((-4.20 41.20, -4.00 41.20, -4.00 41.30, -4.20 41.30, -4.20 41.20))'
        })
        mostrar(f"UPDATE geometría válida — id={id1}", r_upd2)

    # ==========================================================================
    # SECCIÓN 5 — ACTUALIZACIONES RECHAZADAS
    # ==========================================================================
    print("\n>>> SECCIÓN 5: Actualizaciones rechazadas")

    if len(ids_insertados) >= 2:
        id2 = ids_insertados[1]

        # Intentar mover el polígono 2 a una posición que solapa con el polígono 1
        # (después de haberlo movido en la sección 4).
        r_upd_rej1 = z.update({
            'id'  : id2,
            'geom': 'POLYGON((-4.15 41.15, -3.95 41.15, -3.95 41.25, -4.15 41.25, -4.15 41.15))'
        })
        mostrar(f"UPDATE rechazado — nueva geom solapa con id={ids_insertados[0]}", r_upd_rej1)

    # Actualizar un ID que no existe en la base de datos.
    r_upd_rej2 = z.update({
        'id'          : 999999,
        'area_hectareas': 100.00
    })
    mostrar("UPDATE rechazado — id=999999 no existe", r_upd_rej2)

    # Llamada a update sin ningún campo modificable.
    if ids_insertados:
        r_upd_rej3 = z.update({'id': ids_insertados[0]})
        mostrar("UPDATE rechazado — no se enviaron campos a modificar", r_upd_rej3)

    # ==========================================================================
    # SECCIÓN 6 — CONSULTAS (SELECT)
    # ==========================================================================
    print("\n>>> SECCIÓN 6: Consultas SELECT")

    # Todos los registros como lista de tuplas.
    r_sel1 = z.selectAsTuples({})
    mostrar("SELECT todos (tuples)", r_sel1)

    # Todos los registros como lista de diccionarios (más legible).
    r_sel2 = z.selectAsDicts({})
    mostrar("SELECT todos (dicts)", r_sel2)

    # Filtrar por un ID concreto.
    if ids_insertados:
        r_sel3 = z.selectAsDicts({'id': ids_insertados[0]})
        mostrar(f"SELECT por id={ids_insertados[0]} (dicts)", r_sel3)

    # Filtrar por un ID que no existe → devuelve lista vacía, no error.
    r_sel4 = z.selectAsDicts({'id': 999999})
    mostrar("SELECT id=999999 inexistente — lista vacía esperada", r_sel4)

    # ==========================================================================
    # SECCIÓN 7 — ELIMINACIONES
    # ==========================================================================
    print("\n>>> SECCIÓN 7: Eliminaciones")

    # Intentar borrar un ID que no existe.
    r_del_err = z.delete({'id': 999999})
    mostrar("DELETE id=999999 — no existe", r_del_err)

    # Borrar todos los registros que este test insertó.
    print("\n  -- Limpieza: borrando registros insertados en este test --")
    for rid in ids_insertados:
        r_del = z.delete({'id': rid})
        mostrar(f"DELETE id={rid}", r_del)

    # Verificar que la tabla quedó vacía (o al menos sin nuestros registros).
    r_final = z.selectAsTuples({})
    mostrar("SELECT final — debe estar vacía", r_final)

    # Cerramos la conexión a la base de datos.
    z.disconnect()

    print("\n" + "=" * 60)
    print("  FIN DE PRUEBAS — ZonasConservacion")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
