import sys
import os

from estaciones_monitoreo.estaciones_monitoreo_OOP import EstacionesMonitoreo
from red_canales.red_canales_OOP import RedCanales
from zonas_conservacion.zonas_conservacion_OOP import ZonasConservacion

# INSERTS ---------------------------------------------------------------
# -----------------------------------------------------------------------
zonas = ZonasConservacion()
insert_zona = zonas.insert({
        'nombre_area': 'Parque Natural Sierra Norte',
        'categoria_proteccion': 'Parque Natural',
        'entidad_responsable': 'Ministerio de Medio Ambiente',
        'area_hectareas': 5000.00,
        'fecha_declaracion': '2010-06-20',
        'geom': 'POLYGON((-3.80 40.40, -3.60 40.40, -3.60 40.50, -3.80 40.50, -3.80 40.40))'
    })

print(insert_zona)

# --- INSERT rechazado: intersecta con la zona anterior ---
insert_zona_dup = zonas.insert({
        'nombre_area': 'Zona Solapada',
        'categoria_proteccion': 'Reserva',
        'entidad_responsable': 'Gobierno Regional',
        'area_hectareas': 1200.00,
        'fecha_declaracion': '2015-03-01',
        'geom': 'POLYGON((-3.75 40.42, -3.65 40.42, -3.65 40.48, -3.75 40.48, -3.75 40.42))'
    })

print(insert_zona_dup)


canales = RedCanales()
# --- INSERT válido ---
insert_canal = canales.insert({
        'codigo_inventario': 'CAN-001',
        'material_construccion': 'Hormigon',
        'capacidad_caudal': 15.750,
        'ultimo_mantenimiento': '2024-03-10 08:00:00',
        'geom': 'LINESTRING(-3.70 40.41, -3.68 40.43, -3.65 40.45)'
    })
print(insert_canal)
# --- INSERT rechazado: intersecta con el canal anterior ---
insert_canal_dup = canales.insert({
        'codigo_inventario': 'CAN-002',
        'material_construccion': 'PVC',
        'capacidad_caudal': 8.000,
        'ultimo_mantenimiento': '2024-05-01 09:00:00',
        'geom': 'LINESTRING(-3.69 40.40, -3.67 40.44)'
    })
print(insert_canal_dup)




estaciones = EstacionesMonitoreo()
# --- INSERT válido: punto dentro del polígono insertado arriba ---
insert_estacion = estaciones.insert({
    'nombre': 'Estacion Norte A',
    'tipo_sensor': 'Temperatura',
    'fecha_instalacion': '2024-01-15',
    'estado_operativo': True,
    'altitud_msnm': 1200.50,
    'geom': 'POINT(-3.70 40.45)'
})

print(insert_estacion)

# --- INSERT rechazado: punto fuera de cualquier zona de conservación ---
insert_est_out = estaciones.insert({
    'nombre': 'Estacion Exterior',
    'tipo_sensor': 'Humedad',
    'fecha_instalacion': '2024-02-20',
    'estado_operativo': True,
    'altitud_msnm': 800.00,
    'geom': 'POINT(-4.50 41.20)'
})

print(insert_est_out)

