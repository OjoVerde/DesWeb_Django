import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from estaciones_monitoreo.estaciones_monitoreo_OOP import EstacionesMonitoreo
from red_canales.red_canales_OOP import RedCanales
from zonas_conservacion.zonas_conservacion_OOP import ZonasConservacion

SEP = "-" * 60

def print_result(label, result):
    print(f"\n  [{label}]")
    print(f"  ok      : {result['ok']}")
    print(f"  message : {result['message']}")
    print(f"  data    : {result['data']}")

def main():

    # ==================================================================
    # TABLA 3: Zonas de Conservación — debe insertarse PRIMERO porque
    # las estaciones requieren estar dentro de una zona (ST_Within).
    # ==================================================================
    print(f"\n{SEP}")
    print("ZONAS DE CONSERVACIÓN (Polígonos)")
    print(SEP)

    zonas = ZonasConservacion()

    # --- INSERT válido ---
    res_insert_zona = zonas.insert({
        'nombre_area': 'Parque Natural Sierra Norte',
        'categoria_proteccion': 'Parque Natural',
        'entidad_responsable': 'Ministerio de Medio Ambiente',
        'area_hectareas': 5000.00,
        'fecha_declaracion': '2010-06-20',
        'geom': 'POLYGON((-3.80 40.40, -3.60 40.40, -3.60 40.50, -3.80 40.50, -3.80 40.40))'
    })
    print_result("INSERT zona válida", res_insert_zona)
    id_zona = res_insert_zona['data'][0]['id'] if res_insert_zona['ok'] else None

    # --- INSERT rechazado: intersecta con la zona anterior ---
    res_insert_zona_dup = zonas.insert({
        'nombre_area': 'Zona Solapada',
        'categoria_proteccion': 'Reserva',
        'entidad_responsable': 'Gobierno Regional',
        'area_hectareas': 1200.00,
        'fecha_declaracion': '2015-03-01',
        'geom': 'POLYGON((-3.75 40.42, -3.65 40.42, -3.65 40.48, -3.75 40.48, -3.75 40.42))'
    })
    print_result("INSERT zona rechazada (intersecta)", res_insert_zona_dup)

    # --- UPDATE válido (solo atributos, sin cambio de geometría) ---
    if id_zona:
        res_update_zona = zonas.update({
            'id': id_zona,
            'area_hectareas': 5250.75,
            'entidad_responsable': 'Ministerio de Transición Ecológica'
        })
        print_result("UPDATE zona (atributos)", res_update_zona)

    # --- SELECT AS TUPLES ---
    res_tuples_zonas = zonas.selectAsTuples({})
    print_result("SELECT zonas (tuples)", {
        'ok': res_tuples_zonas['ok'],
        'message': res_tuples_zonas['message'],
        'data': res_tuples_zonas['data']
    })

    # --- SELECT AS DICTS ---
    res_dicts_zonas = zonas.selectAsDicts({})
    print_result("SELECT zonas (dicts)", {
        'ok': res_dicts_zonas['ok'],
        'message': res_dicts_zonas['message'],
        'data': res_dicts_zonas['data']
    })

    zonas.disconnect()

    # ==================================================================
    # TABLA 2: Red de Canales (LineStrings)
    # ==================================================================
    print(f"\n{SEP}")
    print("RED DE CANALES (LineStrings)")
    print(SEP)

    canales = RedCanales()

    # --- INSERT válido ---
    res_insert_canal = canales.insert({
        'codigo_inventario': 'CAN-001',
        'material_construccion': 'Hormigon',
        'capacidad_caudal': 15.750,
        'longitud_km': 2.30,
        'ultima_mantenimiento': '2024-03-10 08:00:00',
        'geom': 'LINESTRING(-3.70 40.41, -3.68 40.43, -3.65 40.45)'
    })
    print_result("INSERT canal válido", res_insert_canal)
    id_canal = res_insert_canal['data'][0]['id'] if res_insert_canal['ok'] else None

    # --- INSERT rechazado: intersecta con el canal anterior ---
    res_insert_canal_dup = canales.insert({
        'codigo_inventario': 'CAN-002',
        'material_construccion': 'PVC',
        'capacidad_caudal': 8.000,
        'longitud_km': 1.10,
        'ultima_mantenimiento': '2024-05-01 09:00:00',
        'geom': 'LINESTRING(-3.69 40.40, -3.67 40.44)'
    })
    print_result("INSERT canal rechazado (intersecta)", res_insert_canal_dup)

    # --- UPDATE válido (solo atributos) ---
    if id_canal:
        res_update_canal = canales.update({
            'id': id_canal,
            'capacidad_caudal': 20.000,
            'material_construccion': 'Acero'
        })
        print_result("UPDATE canal (atributos)", res_update_canal)

    # --- SELECT AS TUPLES ---
    res_tuples_canales = canales.selectAsTuples({})
    print_result("SELECT canales (tuples)", {
        'ok': res_tuples_canales['ok'],
        'message': res_tuples_canales['message'],
        'data': res_tuples_canales['data']
    })

    # --- SELECT AS DICTS por id ---
    if id_canal:
        res_dicts_canal = canales.selectAsDicts({'id': id_canal})
        print_result(f"SELECT canal id={id_canal} (dicts)", {
            'ok': res_dicts_canal['ok'],
            'message': res_dicts_canal['message'],
            'data': res_dicts_canal['data']
        })

    canales.disconnect()

    # ==================================================================
    # TABLA 1: Estaciones de Monitoreo (Points)
    # Deben estar dentro de alguna zona de conservación (ST_Within).
    # ==================================================================
    print(f"\n{SEP}")
    print("ESTACIONES DE MONITOREO (Points)")
    print(SEP)

    estaciones = EstacionesMonitoreo()

    # --- INSERT válido: punto dentro del polígono insertado arriba ---
    res_insert_est = estaciones.insert({
        'nombre': 'Estacion Norte A',
        'tipo_sensor': 'Temperatura',
        'fecha_instalacion': '2024-01-15',
        'estado_operativo': True,
        'altitud_msnm': 1200.50,
        'geom': 'POINT(-3.70 40.45)'
    })
    print_result("INSERT estación válida (dentro de zona)", res_insert_est)
    id_est = res_insert_est['data'][0]['id'] if res_insert_est['ok'] else None

    # --- INSERT rechazado: punto fuera de cualquier zona de conservación ---
    res_insert_est_out = estaciones.insert({
        'nombre': 'Estacion Exterior',
        'tipo_sensor': 'Humedad',
        'fecha_instalacion': '2024-02-20',
        'estado_operativo': True,
        'altitud_msnm': 800.00,
        'geom': 'POINT(-4.50 41.20)'
    })
    print_result("INSERT estación rechazada (fuera de zona)", res_insert_est_out)

    # --- UPDATE válido (nombre + altitud) ---
    if id_est:
        res_update_est = estaciones.update({
            'id': id_est,
            'nombre': 'Estacion Norte A - Revisada',
            'altitud_msnm': 1250.00
        })
        print_result("UPDATE estación (atributos)", res_update_est)

    # --- UPDATE rechazado: mover punto fuera de zona ---
    if id_est:
        res_update_est_out = estaciones.update({
            'id': id_est,
            'geom': 'POINT(-5.00 42.00)'
        })
        print_result("UPDATE estación rechazado (geom fuera de zona)", res_update_est_out)

    # --- SELECT AS TUPLES ---
    res_tuples_est = estaciones.selectAsTuples({})
    print_result("SELECT estaciones (tuples)", {
        'ok': res_tuples_est['ok'],
        'message': res_tuples_est['message'],
        'data': res_tuples_est['data']
    })

    # --- SELECT AS DICTS ---
    res_dicts_est = estaciones.selectAsDicts({})
    print_result("SELECT estaciones (dicts)", {
        'ok': res_dicts_est['ok'],
        'message': res_dicts_est['message'],
        'data': res_dicts_est['data']
    })

    # ==================================================================
    # LIMPIEZA: eliminamos los registros de prueba en orden inverso
    # (primero puntos, luego líneas, luego polígonos)
    # ==================================================================
    print(f"\n{SEP}")
    print("LIMPIEZA DE DATOS DE PRUEBA")
    print(SEP)

    if id_est:
        print_result(f"DELETE estación id={id_est}", estaciones.delete({'id': id_est}))

    # DELETE inexistente (prueba de respuesta controlada)
    print_result("DELETE estación inexistente id=9999", estaciones.delete({'id': 9999}))
    estaciones.disconnect()

    if id_canal:
        canales2 = RedCanales()
        print_result(f"DELETE canal id={id_canal}", canales2.delete({'id': id_canal}))
        canales2.disconnect()

    if id_zona:
        zonas2 = ZonasConservacion()
        print_result(f"DELETE zona id={id_zona}", zonas2.delete({'id': id_zona}))
        zonas2.disconnect()

    print(f"\n{SEP}")
    print("FIN DE PRUEBAS")
    print(SEP)


if __name__ == "__main__":
    main()
