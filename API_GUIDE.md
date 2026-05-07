# Guía de API - app_conservacion

## Base URL
```
http://localhost:8000/app_conservacion/
```

## Formato de Respuesta
Todas las respuestas siguen este formato:
```json
{
  "ok": true/false,
  "message": "Descripción del resultado",
  "data": [...] // Resultados o null si hay error
}
```

## Códigos de Estado HTTP
| Código | Descripción |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado |
| 400 | Bad Request - Datos inválidos |
| 500 | Internal Server Error - Error interno |

---

## Endpoints

### 1. Zonas de Conservación (Polígonos)

#### GET - Listar todas (formato dict)
```bash
curl -s "http://localhost:8000/app_conservacion/zonas_conservacion/"
```
**Respuesta:**
```json
{
    "ok": true,
    "message": "2 registro(s) encontrado(s).",
    "data": [
        {
            "id": 1,
            "nombre_area": "Reserva Norte",
            "categoria_proteccion": "Parque Nacional",
            "entidad_responsable": null,
            "area_hectareas": "10000.00",
            "fecha_declaracion": "2010-06-15",
            "geom": "POLYGON ((440000 4470000, 450000 4470000, 450000 4480000, 440000 4480000, 440000 4470000))"
        },
        {
            "id": 4,
            "nombre_area": "Zona Test Actualizada",
            "categoria_proteccion": "Reserva Natural",
            "entidad_responsable": null,
            "area_hectareas": "100.00",
            "fecha_declaracion": null,
            "geom": "POLYGON ((500000 4500000, 501000 4500000, 501000 4501000, 500000 4501000, 500000 4500000))"
        }
    ]
}
```

#### GET - Formato tuplas
```bash
curl -s "http://localhost:8000/app_conservacion/zonas_conservacion/?format=tuple"
```
**Respuesta:**
```json
{
    "ok": true,
    "message": "2 registro(s) encontrado(s).",
    "data": [
        [1, "Reserva Norte", "Parque Nacional", null, "10000.00", "2010-06-15", "POLYGON ((440000 4470000, 450000 4470000, 450000 4480000, 440000 4480000, 440000 4470000))"],
        [4, "Zona Test Actualizada", "Reserva Natural", null, "100.00", null, "POLYGON ((500000 4500000, 501000 4500000, 501000 4501000, 500000 4501000, 500000 4500000))"]
    ]
}
```

#### GET - Por ID
```bash
curl -s "http://localhost:8000/app_conservacion/zonas_conservacion/?id=1"
```
**Respuesta:**
```json
{
    "ok": true,
    "message": "1 registro(s) encontrado(s).",
    "data": [
        {
            "id": 1,
            "nombre_area": "Reserva Norte",
            "categoria_proteccion": "Parque Nacional",
            "entidad_responsable": null,
            "area_hectareas": "10000.00",
            "fecha_declaracion": "2010-06-15",
            "geom": "POLYGON ((440000 4470000, 450000 4470000, 450000 4480000, 440000 4480000, 440000 4470000))"
        }
    ]
}
```

#### POST - Crear nueva zona
```bash
curl -s -X POST "http://localhost:8000/app_conservacion/zonas_conservacion/" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_area": "Parque Natural Sierra de Mariola",
    "categoria_proteccion": "Parque Natural",
    "entidad_responsable": "Generalitat Valenciana",
    "fecha_declaracion": "2022-03-15",
    "geom": "POLYGON((520000 4300000, 530000 4300000, 530000 4310000, 520000 4310000, 520000 4300000))"
  }'
```
**Respuesta (éxito):**
```json
{
    "ok": true,
    "message": "ZonaConservacion id=5 insertada correctamente.",
    "data": [
        {
            "id": 5,
            "nombre_area": "Parque Natural Sierra de Mariola",
            "categoria_proteccion": "Parque Natural",
            "entidad_responsable": "Generalitat Valenciana",
            "area_hectareas": 10000.0,
            "fecha_declaracion": "2022-03-15",
            "geom": "POLYGON ((520000 4300000, 530000 4300000, 530000 4310000, 520000 4310000, 520000 4300000))"
        }
    ]
}
```

#### POST - Error por intersección (geometría que intersecta con zona existente)
```bash
curl -s -X POST "http://localhost:8024/api/app_conservacion/zonas_conservacion/" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_area": "Zona Intersecta",
    "geom": "POLYGON((445000 4475000, 445500 4475000, 445500 4475500, 445000 4475500, 445000 4475000))"
  }'
```
**Respuesta (error):**
```json
{
    "ok": false,
    "message": "Operación rechazada: la geometría intersecta con una zona de conservación existente.",
    "data": null
}
```

#### PUT - Actualizar zona
```bash
curl -s -X PUT "http://localhost:8000/app_conservacion/zonas_conservacion/" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "nombre_area": "Reserva Norte Actualizada",
    "categoria_proteccion": "Parque Nacional Regional"
  }'
```
**Respuesta:**
```json
{
    "ok": true,
    "message": "ZonaConservacion id=1 actualizada correctamente.",
    "data": [
        {
            "id": 1,
            "nombre_area": "Reserva Norte Actualizada",
            "categoria_proteccion": "Parque Nacional Regional",
            "entidad_responsable": null,
            "area_hectareas": "10000.00",
            "fecha_declaracion": "2010-06-15",
            "geom": "POLYGON ((440000 4470000, 450000 4470000, 450000 4480000, 440000 4480000, 440000 4470000))"
        }
    ]
}
```

#### DELETE - Eliminar zona
```bash
curl -s -X DELETE "http://localhost:8000/app_conservacion/zonas_conservacion/" \
  -H "Content-Type: application/json" \
  -d '{"id": 4}'
```
**Respuesta:**
```json
{
    "ok": true,
    "message": "ZonaConservacion id=4 eliminada correctamente.",
    "data": null
}
```

---

### 2. Red de Canales (LineStrings)

#### GET - Listar todos (formato dict)
```bash
curl -s "http://localhost:8000/app_conservacion/red_canales/"
```
**Respuesta:**
```json
{
    "ok": true,
    "message": "1 registro(s) encontrado(s).",
    "data": [
        {
            "id": 2,
            "codigo_inventario": "RN-3742",
            "material_construccion": "Concreto",
            "capacidad_caudal": "400.000",
            "longitud_m": "0.74",
            "ultimo_mantenimiento": "2024-02-01T00:00:00Z",
            "geom": "LINESTRING (442118.8 4474396.2, 441691.3 4473795.8)"
        }
    ]
}
```

#### GET - Formato tuplas
```bash
curl -s "http://localhost:8000/app_conservacion/red_canales/?format=tuple"
```
**Respuesta:**
```json
{
    "ok": true,
    "message": "1 registro(s) encontrado(s).",
    "data": [
        [2, "RN-3742", "Concreto", "400.000", "0.74", "2024-02-01T00:00:00Z", "LINESTRING (442118.8 4474396.2, 441691.3 4473795.8)"]
    ]
}
```

#### GET - Por ID
```bash
curl -s "http://localhost:8000/app_conservacion/red_canales/?id=2"
```

#### POST - Crear nuevo canal
```bash
curl -s -X POST "http://localhost:8000/app_conservacion/red_canales/" \
  -H "Content-Type: application/json" \
  -d '{
    "codigo_inventario": "CAN-NEW-001",
    "material_construccion": "Hormigon",
    "capacidad_caudal": 25.500,
    "ultimo_mantenimiento": "2024-06-15T10:00:00",
    "geom": "LINESTRING(520000 4305000, 521000 4308000, 522000 4310000)"
  }'
```
**Respuesta:**
```json
{
    "ok": true,
    "message": "RedCanal id=7 insertado correctamente.",
    "data": [
        {
            "id": 7,
            "codigo_inventario": "CAN-NEW-001",
            "material_construccion": "Hormigon",
            "capacidad_caudal": "25.500",
            "longitud_m": "1.414",
            "ultimo_mantenimiento": "2024-06-15T10:00:00",
            "geom": "LINESTRING (520000 4305000, 521000 4308000, 522000 4310000)"
        }
    ]
}
```

#### PUT - Actualizar canal
```bash
curl -s -X PUT "http://localhost:8000/app_conservacion/red_canales/" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 2,
    "material_construccion": "Hormigon armado",
    "capacidad_caudal": 450.000
  }'
```
**Respuesta:**
```json
{
    "ok": true,
    "message": "RedCanal id=2 actualizado correctamente.",
    "data": [
        {
            "id": 2,
            "codigo_inventario": "RN-3742",
            "material_construccion": "Hormigon armado",
            "capacidad_caudal": "450.000",
            "longitud_m": "0.74",
            "ultimo_mantenimiento": "2024-02-01T00:00:00Z",
            "geom": "LINESTRING (442118.8 4474396.2, 441691.3 4473795.8)"
        }
    ]
}
```

#### DELETE - Eliminar canal
```bash
curl -s -X DELETE "http://localhost:8000/app_conservacion/red_canales/" \
  -H "Content-Type: application/json" \
  -d '{"id": 7}'
```
**Respuesta:**
```json
{
    "ok": true,
    "message": "RedCanal id=7 eliminado correctamente.",
    "data": null
}
```

---

### 3. Estaciones de Monitoreo (Puntos)

**Nota**: Las estaciones deben estar dentro de una zona de conservación existente.

#### GET - Listar todas (formato dict)
```bash
curl -s "http://localhost:8000/app_conservacion/estaciones_monitoreo/"
```
**Respuesta:**
```json
{
    "ok": true,
    "message": "3 registro(s) encontrado(s).",
    "data": [
        {
            "id": 1,
            "nombre": "Estacion Alpha",
            "tipo_sensor": "Temperatura",
            "fecha_instalacion": "2021-05-10",
            "estado_operativo": true,
            "altitud_msnm": "320.50",
            "geom": "POINT (442118.8 4474396.2)"
        },
        {
            "id": 4,
            "nombre": "Sin nombre (debe fallar)",
            "tipo_sensor": null,
            "fecha_instalacion": null,
            "estado_operativo": true,
            "altitud_msnm": null,
            "geom": "POINT (-2.5 39.5)"
        },
        {
            "id": 5,
            "nombre": "Estacion Test Nueva",
            "tipo_sensor": "Presion",
            "fecha_instalacion": null,
            "estado_operativo": true,
            "altitud_msnm": null,
            "geom": "POINT (500500 4500300)"
        }
    ]
}
```

#### GET - Formato tuplas
```bash
curl -s "http://localhost:8000/app_conservacion/estaciones_monitoreo/?format=tuple"
```
**Respuesta:**
```json
{
    "ok": true,
    "message": "3 registro(s) encontrado(s).",
    "data": [
        [1, "Estacion Alpha", "Temperatura", "2021-05-10", true, "320.50", "POINT (442118.8 4474396.2)"],
        [4, "Sin nombre (debe fallar)", null, null, true, null, "POINT (-2.5 39.5)"],
        [5, "Estacion Test Nueva", "Presion", null, true, null, "POINT (500500 4500300)"]
    ]
}
```

#### GET - Por ID
```bash
curl -s "http://localhost:8000/app_conservacion/estaciones_monitoreo/?id=1"
```

#### POST - Crear nueva estación (dentro de zona de conservación)
```bash
curl -s -X POST "http://localhost:8000/app_conservacion/estaciones_monitoreo/" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Estacion Meteorologica Sierra Norte",
    "tipo_sensor": "Temperatura-Humedad",
    "fecha_instalacion": "2023-06-01",
    "estado_operativo": true,
    "altitud_msnm": 850.50,
    "geom": "POINT(520000 4305000)"
  }'
```
**Respuesta:**
```json
{
    "ok": true,
    "message": "EstacionMonitoreo id=6 insertada correctamente.",
    "data": [
        {
            "id": 6,
            "nombre": "Estacion Meteorologica Sierra Norte",
            "tipo_sensor": "Temperatura-Humedad",
            "fecha_instalacion": "2023-06-01",
            "estado_operativo": true,
            "altitud_msnm": "850.50",
            "geom": "POINT (520000 4305000)"
        }
    ]
}
```

#### POST - Error (punto fuera de zona de conservación)
```bash
curl -s -X POST "http://localhost:8000/app_conservacion/estaciones_monitoreo/" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Estacion Fuera de Zona",
    "tipo_sensor": "Presion",
    "geom": "POINT(100000 4000000)"
  }'
```
**Respuesta (error):**
```json
{
    "ok": false,
    "message": "Operación rechazada: el punto no está dentro de ninguna zona de conservación (ST_Within).",
    "data": null
}
```

#### PUT - Actualizar estación
```bash
curl -s -X PUT "http://localhost:8000/app_conservacion/estaciones_monitoreo/" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "nombre": "Estacion Alpha Actualizada",
    "estado_operativo": false
  }'
```
**Respuesta:**
```json
{
    "ok": true,
    "message": "EstacionMonitoreo id=1 actualizada correctamente.",
    "data": [
        {
            "id": 1,
            "nombre": "Estacion Alpha Actualizada",
            "tipo_sensor": "Temperatura",
            "fecha_instalacion": "2021-05-10",
            "estado_operativo": false,
            "altitud_msnm": "320.50",
            "geom": "POINT (442118.8 4474396.2)"
        }
    ]
}
```

#### DELETE - Eliminar estación
```bash
curl -s -X DELETE "http://localhost:8000/app_conservacion/estaciones_monitoreo/" \
  -H "Content-Type: application/json" \
  -d '{"id": 6}'
```
**Respuesta:**
```json
{
    "ok": true,
    "message": "EstacionMonitoreo id=6 eliminada correctamente.",
    "data": null
}
```

---

## Ejemplos con Python (requests)

### GET - Listar zonas de conservación
```python
import requests

response = requests.get("http://localhost:8000/app_conservacion/zonas_conservacion/")
print(response.json())
```

### GET - Filtrar por ID y formato tuple
```python
import requests

response = requests.get(
    "http://localhost:8000/app_conservacion/zonas_conservacion/",
    params={"id": 1, "format": "tuple"}
)
print(response.json())
```

### POST - Crear zona de conservación
```python
import requests

data = {
    "nombre_area": "Reserva Natural Test",
    "categoria_proteccion": "Reserva Natural",
    "entidad_responsable": "Ayuntamiento",
    "fecha_declaracion": "2024-01-15",
    "geom": "POLYGON((510000 4310000, 511000 4310000, 511000 4311000, 510000 4311000, 510000 4310000))"
}

response = requests.post(
    "http://localhost:8000/app_conservacion/zonas_conservacion/",
    json=data
)
print(f"Status: {response.status_code}")
print(response.json())
```

### PUT - Actualizar canal
```python
import requests

data = {
    "id": 2,
    "material_construccion": "Hormigon preco",
    "capacidad_caudal": 500.000
}

response = requests.put(
    "http://localhost:8000/app_conservacion/red_canales/",
    json=data
)
print(response.json())
```

### DELETE - Eliminar estación
```python
import requests

response = requests.delete(
    "http://localhost:8000/app_conservacion/estaciones_monitoreo/",
    json={"id": 1}
)
print(response.json())
```

---

## Validaciones Espaciales

### Zonas de Conservación
- La geometría debe ser un **Polygon** válido
- No puede intersectarse con otras zonas existentes
- Si intentas crear una zona que interseca con otra, recibirás error 400

### Red de Canales
- La geometría debe ser un **LineString** válido
- No puede intersectarse con otros canales existentes
- La longitud se calcula automáticamente en metros

### Estaciones de Monitoreo
- La geometría debe ser un **Point** válido
- El punto debe estar **dentro** de una zona de conservación existente (ST_Within)
- Si el punto no está dentro de ninguna zona, recibirás error 400

---

## Notas Importantes

1. **WKT Format**: Las geometrías se envían en formato WKT (Well-Known Text)
2. **SRID**: El sistema de coordenadas usado es **25830** (ETRS89 / UTM zone 30N)
3. **CSRF**: Los endpoints están exentos de CSRF para facilitar pruebas
4. **Sin autenticación**: Los endpoints son públicos por defecto
5. **Cálculo automático**: Al crear zonas, el área se calcula automáticamente en hectáreas. Al crear canales, la longitud se calcula automáticamente en metros.
6. **Parámetro format**: Usa `?format=tuple` para obtener resultados como arrays en lugar de diccionarios.