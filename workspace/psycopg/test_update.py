import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from estaciones_monitoreo.estaciones_monitoreo_OOP import EstacionesMonitoreo
from red_canales.red_canales_OOP import RedCanales
from zonas_conservacion.zonas_conservacion_OOP import ZonasConservacion

zonas = ZonasConservacion()
insert_zona = zonas.insert({
        'nombre_area': 'Parque Natural Sierra Norte',
        'categoria_proteccion': 'Parque Natural',
        'entidad_responsable': 'Ministerio de Medio Ambiente',
        'area_hectareas': 5000.00,
        'fecha_declaracion': '2010-06-20',
        'geom': 'POLYGON((-3.80 40.40, -3.60 40.40, -3.60 40.50, -3.80 40.50, -3.80 40.40))'
    })

update_z = zonas.update({
            'nombre_area': 'Parque Natural Sierra SUR',
            'categoria_proteccion': 'Parque Natural',
            'geom':   'POLYGON((-4.15 41.15, -3.95 41.15, -3.95 41.25, -4.15 41.25, -4.15 41.15))'
        })