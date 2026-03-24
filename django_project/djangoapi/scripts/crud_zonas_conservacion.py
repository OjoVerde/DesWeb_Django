from django.db import connection
from django.forms.models import model_to_dict
from django.contrib.gis.geos import GEOSGeometry

from app_conservacion.models import ZonaConservacion


def _geom_to_wkt(instance):
    """Convierte model_to_dict añadiendo geom como WKT string."""
    d = model_to_dict(instance)
    if instance.geom:
        d['geom'] = instance.geom.wkt
    return d


class ZonaConservacionCRUD:
    """
    Clase CRUD para la capa de Zonas de Conservación (Polígonos).

    Validaciones espaciales aplicadas antes de INSERT/UPDATE:
      - ST_SnapToGrid  → redondea coordenadas a 0.0001 grados
      - ST_IsValid     → rechaza geometrías inválidas
      - ST_Intersects  → rechaza polígonos que se solapen con registros existentes
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

    def _has_intersection(self, wkt, exclude_id=None):
        """
        Devuelve True si el polígono intersecta con algún registro existente.
        exclude_id permite omitir el propio registro durante un UPDATE.
        """
        with connection.cursor() as cur:
            if exclude_id is not None:
                cur.execute(
                    """
                    SELECT EXISTS(
                        SELECT 1 FROM eval_01.zonas_conservacion
                        WHERE id != %s
                          AND public.ST_Intersects(geom, public.ST_GeomFromText(%s, 4326))
                    )
                    """,
                    [exclude_id, wkt]
                )
            else:
                cur.execute(
                    """
                    SELECT EXISTS(
                        SELECT 1 FROM eval_01.zonas_conservacion
                        WHERE public.ST_Intersects(geom, public.ST_GeomFromText(%s, 4326))
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
        Inserta una nueva ZonaConservacion.

        Parámetros esperados en data:
            nombre_area (str)           – obligatorio
            geom        (str, WKT)      – obligatorio, Polygon SRID 4326
            categoria_proteccion (str)  – opcional
            entidad_responsable  (str)  – opcional
            area_hectareas       (num)  – opcional
            fecha_declaracion    (str)  – opcional, formato YYYY-MM-DD
        """
        try:
            wkt = data.get('geom')
            if not wkt:
                return {"ok": False, "message": "El campo 'geom' (WKT) es obligatorio.", "data": None}
            if not data.get('nombre_area'):
                return {"ok": False, "message": "El campo 'nombre_area' es obligatorio.", "data": None}

            snapped_wkt, error = self._snap_and_validate(wkt)
            if error:
                return {"ok": False, "message": error, "data": None}

            if self._has_intersection(snapped_wkt):
                return {
                    "ok": False,
                    "message": "Operación rechazada: la geometría intersecta con una zona de conservación existente.",
                    "data": None
                }

            zona = ZonaConservacion(
                nombre_area=data['nombre_area'],
                categoria_proteccion=data.get('categoria_proteccion'),
                entidad_responsable=data.get('entidad_responsable'),
                area_hectareas=data.get('area_hectareas'),
                fecha_declaracion=data.get('fecha_declaracion'),
                geom=GEOSGeometry(snapped_wkt, srid=4326)
            )
            zona.save()

            return {
                "ok": True,
                "message": f"ZonaConservacion id={zona.id} insertada correctamente.",
                "data": [_geom_to_wkt(zona)]
            }

        except Exception as e:
            return {"ok": False, "message": str(e), "data": None}

    def update(self, data: dict) -> dict:
        """
        Actualiza los campos indicados de una ZonaConservacion existente.

        Parámetros esperados en data:
            id (int) – obligatorio
            + cualquier campo a modificar
        """
        try:
            record_id = data.get('id')
            if not record_id:
                return {"ok": False, "message": "El campo 'id' es obligatorio para actualizar.", "data": None}

            try:
                zona = ZonaConservacion.objects.get(pk=record_id)
            except ZonaConservacion.DoesNotExist:
                return {"ok": False, "message": f"No existe ZonaConservacion con id={record_id}.", "data": None}

            wkt = data.get('geom')
            if wkt:
                snapped_wkt, error = self._snap_and_validate(wkt)
                if error:
                    return {"ok": False, "message": error, "data": None}
                if self._has_intersection(snapped_wkt, exclude_id=record_id):
                    return {
                        "ok": False,
                        "message": "Operación rechazada: la geometría actualizada intersecta con otra zona existente.",
                        "data": None
                    }
                zona.geom = GEOSGeometry(snapped_wkt, srid=4326)

            for field in ['nombre_area', 'categoria_proteccion', 'entidad_responsable',
                          'area_hectareas', 'fecha_declaracion']:
                if field in data:
                    setattr(zona, field, data[field])

            zona.save()

            return {
                "ok": True,
                "message": f"ZonaConservacion id={zona.id} actualizada correctamente.",
                "data": [_geom_to_wkt(zona)]
            }

        except Exception as e:
            return {"ok": False, "message": str(e), "data": None}

    def delete(self, data: dict) -> dict:
        """
        Elimina una ZonaConservacion por su id.

        Parámetros esperados en data:
            id (int) – obligatorio
        """
        try:
            record_id = data.get('id')
            if not record_id:
                return {"ok": False, "message": "El campo 'id' es obligatorio para eliminar.", "data": None}

            try:
                zona = ZonaConservacion.objects.get(pk=record_id)
            except ZonaConservacion.DoesNotExist:
                return {"ok": False, "message": f"No existe ZonaConservacion con id={record_id}.", "data": None}

            zona.delete()

            return {
                "ok": True,
                "message": f"ZonaConservacion id={record_id} eliminada correctamente.",
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
            qs = ZonaConservacion.objects.all()
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
            qs = ZonaConservacion.objects.all()
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
