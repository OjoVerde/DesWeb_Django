# Permite que Python encuentre los módulos locales (myLib, estaciones_monitoreo, etc.)
# independientemente del directorio desde donde se ejecute el script
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Importamos las clases OOP de cada tabla
from estaciones_monitoreo.estaciones_monitoreo_OOP import EstacionesMonitoreo
from red_canales.red_canales_OOP import RedCanales
from zonas_conservacion.zonas_conservacion_OOP import ZonasConservacion

def main():

    # =========================================================
    # TABLA 1: Estaciones de Monitoreo (geometría tipo POINT)
    # =========================================================
    print("\n=== Estaciones de Monitoreo ===")

    # Crea una instancia: abre conexión a la BD y crea el cursor
    estaciones = EstacionesMonitoreo()

    # Inserta un registro de prueba con una geometría WKT tipo POINT
    # Devuelve el id generado automáticamente por la BD (RETURNING id)
    id_est = estaciones.insert(
        nombre="Estacion Norte",
        tipo="Temperatura",
        fecha="2024-01-15",
        estado=True,
        altitud=1200.50,
        wkt_geom="POINT(-3.7038 40.4168)"
    )

    # Actualiza el nombre del registro recién insertado usando su id
    estaciones.update(id_est, "Estacion Norte - Actualizada")

    # Consulta todos los registros y los muestra como lista de tuplas
    print("Tuples:", estaciones.selectAsTuples())

    # Consulta todos los registros y los muestra como lista de diccionarios
    print("Dicts:", estaciones.selectAsDicts())

    # Elimina el registro de prueba para no dejar datos basura en la BD
    estaciones.delete(id_est)

    # Cierra el cursor y la conexión a la BD
    estaciones.disconnect()

    # =========================================================
    # TABLA 2: Red de Canales (geometría tipo LINESTRING)
    # =========================================================
    print("\n=== Red de Canales ===")

    # Crea una instancia: abre conexión a la BD y crea el cursor
    canales = RedCanales()

    # Inserta un canal de prueba con una geometría WKT tipo LINESTRING
    # Devuelve el id generado automáticamente por la BD (RETURNING id)
    id_canal = canales.insert(
        codigo="CAN-001",
        material="Hormigon",
        caudal=15.750,
        longitud=2.30,
        fecha_mant="2024-03-10 08:00:00",
        wkt_geom="LINESTRING(-3.70 40.41, -3.68 40.43, -3.65 40.45)"
    )

    # Actualiza la capacidad de caudal del canal recién insertado
    canales.update(id_canal, 20.000)

    # Consulta todos los registros y los muestra como lista de tuplas
    print("Tuples:", canales.selectAsTuples())

    # Consulta todos los registros y los muestra como lista de diccionarios
    print("Dicts:", canales.selectAsDicts())

    # Elimina el registro de prueba para no dejar datos basura en la BD
    canales.delete(id_canal)

    # Cierra el cursor y la conexión a la BD
    canales.disconnect()

    # =========================================================
    # TABLA 3: Zonas de Conservacion (geometría tipo POLYGON)
    # =========================================================
    print("\n=== Zonas de Conservacion ===")

    # Crea una instancia: abre conexión a la BD y crea el cursor
    zonas = ZonasConservacion()

    # Inserta una zona de prueba con una geometría WKT tipo POLYGON
    # El polígono se cierra repitiendo el primer punto al final
    # Devuelve el id generado automáticamente por la BD (RETURNING id)
    id_zona = zonas.insert(
        nombre="Parque Natural Sierra",
        categoria="Parque Natural",
        entidad="Ministerio de Medio Ambiente",
        area=5000.00,
        fecha_dec="2010-06-20",
        wkt_geom="POLYGON((-3.80 40.40, -3.60 40.40, -3.60 40.50, -3.80 40.50, -3.80 40.40))"
    )

    # Actualiza el área en hectáreas de la zona recién insertada
    zonas.update(id_zona, 5100.00)

    # Consulta todos los registros y los muestra como lista de tuplas
    print("Tuples:", zonas.selectAsTuples())

    # Consulta todos los registros y los muestra como lista de diccionarios
    print("Dicts:", zonas.selectAsDicts())

    # Elimina el registro de prueba para no dejar datos basura en la BD
    zonas.delete(id_zona)

    # Cierra el cursor y la conexión a la BD
    zonas.disconnect()

# Punto de entrada del script: solo ejecuta main() si se corre directamente
# (no cuando se importa como módulo desde otro archivo)
if __name__ == "__main__":
    main()
