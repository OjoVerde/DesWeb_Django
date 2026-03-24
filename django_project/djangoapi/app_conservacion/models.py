from django.contrib.gis.db import models


class ZonaConservacion(models.Model):
    nombre_area = models.CharField(max_length=150)
    categoria_proteccion = models.CharField(max_length=100, null=True, blank=True)
    entidad_responsable = models.CharField(max_length=100, null=True, blank=True)
    area_hectareas = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    fecha_declaracion = models.DateField(null=True, blank=True)
    geom = models.PolygonField(srid=4326, null=True, blank=True)

    class Meta:
        db_table = '"eval_01"."zonas_conservacion"'
        managed = False


class RedCanal(models.Model):
    codigo_inventario = models.CharField(max_length=20, unique=True, null=True, blank=True)
    material_construccion = models.CharField(max_length=50, null=True, blank=True)
    capacidad_caudal = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    longitud_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ultima_mantenimiento = models.DateTimeField(null=True, blank=True)
    geom = models.LineStringField(srid=4326, null=True, blank=True)

    class Meta:
        db_table = '"eval_01"."red_canales"'
        managed = False


class EstacionMonitoreo(models.Model):
    nombre = models.CharField(max_length=100)
    tipo_sensor = models.CharField(max_length=50, null=True, blank=True)
    fecha_instalacion = models.DateField(null=True, blank=True)
    estado_operativo = models.BooleanField(default=True)
    altitud_msnm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    geom = models.PointField(srid=4326, null=True, blank=True)

    class Meta:
        db_table = '"eval_01"."estaciones_monitoreo"'
        managed = False
