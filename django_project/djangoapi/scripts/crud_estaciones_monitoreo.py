from django.db import connection
from django.forms.models import model_to_dict
from django.contrib.gis.geos import GEOSGeometry

from app_conservacion.models import EstacionMonitoreo


def _geom_to_wkt(instance):
    """Convierte model_to_dict añadiendo geom como WKT string."""
    d = model_to_dict(instance)
    if instance.geom:
        d['geom'] = instance.geom.wkt
    return d


class EstacionMonitoreoCRUD:
    """
    Clase CRUD para la capa de Estaciones de Monitoreo (Puntos).

    Validaciones espaciales aplicadas antes de INSERT/UPDATE:
      - ST_SnapToGrid  → redondea coordenadas a 0.0001 grados
      - ST_IsValid     → rechaza geometrías inválidas
      - ST_Within      → rechaza puntos que no estén dentro de alguna
                         zona de conservación existente
    """

    # ------------------------------------------------------------------ #
    #  Helpers privados de validación espacial                            #
    # ------------------------------------------------------------------ #

    def _snap_and_validate(self, wkt):
        """
        Redondea las coordenadas con ST_SnapToGrid y verifica ST_IsValid.

        Retorna:
            (snapped_wkt: str, error: str | None)
        """
        with connection.cursor() as cur:
            cur.execute(
                """
                SELECT
                    public.ST_AsText(public.ST_SnapToGrid(public.ST_GeomFromText(%s, 4326), 0.0001)),
                    public.ST_IsValid(public.ST_SnapToGrid(public.ST_GeomFromText(%s, 4326), 0.0001))
                """,
                [wkt, wkt]
            )
            row = cur.fetchone()

        if row is None or row[0] is None:
            return None, "No se pudo procesar la geometría WKT proporcionada."

        snapped_wkt, is_valid = row
        if not is_valid:
            return None, "La geometría no es válida tras aplicar ST_SnapToGrid."

        return snapped_wkt, None

    def _is_within_zona(self, wkt):
        """
        Devuelve True si el punto está estrictamente dentro de al menos
        una zona de conservación (ST_Within, excluye el borde del polígono).
        """
        with connection.cursor() as cur:
            cur.execute(
                """
                SELECT EXISTS(
                    SELECT 1 FROM eval_01.zonas_conservacion
                    WHERE public.ST_Within(public.ST_GeomFromText(%s, 4326), geom)
                )
                """,
                [wkt]
            )
            return cur.fetchone()[0]

    # ------------------------------------------------------------------ #
    #  Métodos CRUD                                                       #
    # ------------------------------------------------------------------ #

    def insert(self, data: dict) -> dict:
        """
        Inserta una nueva EstacionMonitoreo.

        Parámetros esperados en data:
            nombre            (str)       – obligatorio
            geom              (str, WKT)  – obligatorio, Point SRID 4326
            tipo_sensor       (str)       – opcional
            fecha_instalacion (str)       – opcional, formato YYYY-MM-DD
            estado_operativo  (bool)      – opcional, default True
            altitud_msnm      (num)       – opcional
        """
        try:
            wkt = data.get('geom')
            if not wkt:
                return {"ok": False, "message": "El campo 'geom' (WKT) es obligatorio.", "data": None}
            if not data.get('nombre'):
                return {"ok": False, "message": "El campo 'nombre' es obligatorio.", "data": None}

            snapped_wkt, error = self._snap_and_validate(wkt)
            if error:
                return {"ok": False, "message": error, "data": None}

            if not self._is_within_zona(snapped_wkt):
                return {
                    "ok": False,
                    "message": "Operación rechazada: el punto no está dentro de ninguna zona de conservación (ST_Within).",
                    "data": None
                }

            estacion = EstacionMonitoreo(
                nombre=data['nombre'],
                tipo_sensor=data.get('tipo_sensor'),
                fecha_instalacion=data.get('fecha_instalacion'),
                estado_operativo=data.get('estado_operativo', True),
                altitud_msnm=data.get('altitud_msnm'),
                geom=GEOSGeometry(snapped_wkt, srid=4326)
            )
            estacion.save()

            return {
                "ok": True,
                "message": f"EstacionMonitoreo id={estacion.id} insertada correctamente.",
                "data": [_geom_to_wkt(estacion)]
            }

        except Exception as e:
            return {"ok": False, "message": str(e), "data": None}

    def update(self, data: dict) -> dict:
        """
        Actualiza los campos indicados de una EstacionMonitoreo existente.

        Parámetros esperados en data:
            id (int) – obligatorio
            + cualquier campo a modificar
        """
        try:
            record_id = data.get('id')
            if not record_id:
                return {"ok": False, "message": "El campo 'id' es obligatorio para actualizar.", "data": None}

            try:
                estacion = EstacionMonitoreo.objects.get(pk=record_id)
            except EstacionMonitoreo.DoesNotExist:
                return {"ok": False, "message": f"No existe EstacionMonitoreo con id={record_id}.", "data": None}

            wkt = data.get('geom')
            if wkt:
                snapped_wkt, error = self._snap_and_validate(wkt)
                if error:
                    return {"ok": False, "message": error, "data": None}
                if not self._is_within_zona(snapped_wkt):
                    return {
                        "ok": False,
                        "message": "Operación rechazada: el punto actualizado no está dentro de ninguna zona de conservación.",
                        "data": None
                    }
                estacion.geom = GEOSGeometry(snapped_wkt, srid=4326)

            for field in ['nombre', 'tipo_sensor', 'fecha_instalacion',
                          'estado_operativo', 'altitud_msnm']:
                if field in data:
                    setattr(estacion, field, data[field])

            estacion.save()

            return {
                "ok": True,
                "message": f"EstacionMonitoreo id={estacion.id} actualizada correctamente.",
                "data": [_geom_to_wkt(estacion)]
            }

        except Exception as e:
            return {"ok": False, "message": str(e), "data": None}

    def delete(self, data: dict) -> dict:
        """
        Elimina una EstacionMonitoreo por su id.

        Parámetros esperados en data:
            id (int) – obligatorio
        """
        try:
            record_id = data.get('id')
            if not record_id:
                return {"ok": False, "message": "El campo 'id' es obligatorio para eliminar.", "data": None}

            try:
                estacion = EstacionMonitoreo.objects.get(pk=record_id)
            except EstacionMonitoreo.DoesNotExist:
                return {"ok": False, "message": f"No existe EstacionMonitoreo con id={record_id}.", "data": None}

            estacion.delete()

            return {
                "ok": True,
                "message": f"EstacionMonitoreo id={record_id} eliminada correctamente.",
                "data": None
            }

        except Exception as e:
            return {"ok": False, "message": str(e), "data": None}

    def selectAsDicts(self, data: dict = None) -> dict:
        """
        Retorna registros como lista de diccionarios (usa model_to_dict).

        Parámetros opcionales en data:
            id (int) – filtra por id específico
        """
        try:
            qs = EstacionMonitoreo.objects.all()
            if data and data.get('id'):
                qs = qs.filter(pk=data['id'])

            result = [_geom_to_wkt(obj) for obj in qs]

            return {
                "ok": True,
                "message": f"{len(result)} registro(s) encontrado(s).",
                "data": result
            }

        except Exception as e:
            return {"ok": False, "message": str(e), "data": None}

    def selectAsTuples(self, data: dict = None) -> dict:
        """
        Retorna registros como lista de tuplas (usa .values_list()).

        Parámetros opcionales en data:
            id (int) – filtra por id específico
        """
        try:
            qs = EstacionMonitoreo.objects.all()
            if data and data.get('id'):
                qs = qs.filter(pk=data['id'])

            result = list(qs.values_list())

            return {
                "ok": True,
                "message": f"{len(result)} registro(s) encontrado(s).",
                "data": result
            }

        except Exception as e:
            return {"ok": False, "message": str(e), "data": None}
