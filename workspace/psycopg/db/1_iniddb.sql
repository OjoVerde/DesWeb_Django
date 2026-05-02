BEGIN;
    -- Creación de la extensión PostGIS
    CREATE EXTENSION IF NOT EXISTS postgis;

    -- Tabla 1: Estaciones de Monitoreo (Puntos)
    -- Representa ubicaciones fijas donde se recolectan datos ambientales.
    CREATE TABLE estaciones_monitoreo (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        tipo_sensor VARCHAR(50),
        fecha_instalacion DATE,
        estado_operativo BOOLEAN DEFAULT TRUE,
        altitud_msnm NUMERIC(10, 2),
        geom GEOMETRY(Point, 25830)
    );

    -- Tabla 2: Red de Canales (Líneas)
    -- Representa la infraestructura hídrica o rutas de transporte.
    CREATE TABLE red_canales (
        id SERIAL PRIMARY KEY,
        codigo_inventario VARCHAR(20) UNIQUE,
        material_construccion VARCHAR(50),
        capacidad_caudal NUMERIC(12, 3),
        longitud_m NUMERIC(10, 2),
        ultimo_mantenimiento TIMESTAMP,
        geom GEOMETRY(LineString, 25830)
    );

    -- Tabla 3: Zonas de Conservación (Polígonos)
    -- Representa áreas protegidas o parcelas de estudio.
    CREATE TABLE zonas_conservacion (
        id SERIAL PRIMARY KEY,
        nombre_area VARCHAR(150) NOT NULL,
        categoria_proteccion VARCHAR(100),
        entidad_responsable VARCHAR(100),
        area_hectareas NUMERIC(15, 2),
        fecha_declaracion DATE,
        geom GEOMETRY(Polygon, 25830)
    );

    -- Índices espaciales para optimizar consultas
    CREATE INDEX idx_estaciones_geom ON estaciones_monitoreo USING GIST (geom);
    CREATE INDEX idx_canales_geom ON red_canales USING GIST (geom);
    CREATE INDEX idx_zonas_geom ON zonas_conservacion USING GIST (geom);
END;