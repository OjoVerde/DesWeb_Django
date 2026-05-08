from django.db import connection
from django.forms.models import model_to_dict
from django.contrib.gis.geos import GEOSGeometry

from app_conservacion.models import RedCanal


def _geom_to_wkt(instance):
    """Convierte model_to_dict añadiendo geom como WKT string."""
    d = model_to_dict(instance)
    if instance.geom:
        d['geom'] = instance.geom.wkt
    return d


class RedCanalCRUD:
    """
    Clase CRUD para la capa de Red de Canales (LineStrings).

    Validaciones espaciales aplicadas antes de INSERT/UPDATE:
      - ST_SnapToGrid  → redondea coordenadas a 0.0001 grados
      - ST_IsValid     → rechaza geometrías inválidas
      - ST_Intersects  → rechaza líneas que se crucen con registros existentes
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
                    public.ST_AsText(public.ST_SnapToGrid(public.ST_GeomFromText(%s, 25830), 0.0001)),
                    public.ST_IsValid(public.ST_SnapToGrid(public.ST_GeomFromText(%s, 25830), 0.0001))
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
        Devuelve True si la línea intersecta con algún registro existente.
        exclude_id permite omitir el propio registro durante un UPDATE.
        """
        with connection.cursor() as cur:
            if exclude_id is not None:
                cur.execute(
                    """
                    SELECT EXISTS(
                        SELECT 1 FROM red_canales
                        WHERE id != %s
                          AND public.ST_Intersects(geom, public.ST_GeomFromText(%s, 25830))
                    )
                    """,
                    [exclude_id, wkt]
                )
            else:
                cur.execute(
                    """
                    SELECT EXISTS(
                        SELECT 1 FROM red_canales
                        WHERE public.ST_Intersects(geom, public.ST_GeomFromText(%s, 25830))
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
        Inserta un nuevo RedCanal.

        Parámetros esperados en data:
            geom                  (str, WKT)  – obligatorio, LineString SRID 25830
            codigo_inventario     (str)        – opcional, único
            material_construccion (str)        – opcional
            capacidad_caudal      (num)        – opcional
            longitud_m           (num)        – opcional
            ultimo_mantenimiento  (str)        – opcional, ISO datetime
        """
        try:
            wkt = data.get('geom')
            if not wkt:
                return {"ok": False, "message": "El campo 'geom' (WKT) es obligatorio.", "data": None}

            snapped_wkt, error = self._snap_and_validate(wkt)
            if error:
                return {"ok": False, "message": error, "data": None}

            if self._has_intersection(snapped_wkt):
                return {
                    "ok": False,
                    "message": "Operación rechazada: la línea intersecta con un canal existente.",
                    "data": None
                }

            geom = GEOSGeometry(snapped_wkt, srid=25830)
            length_m = geom.length / 1000
            canal = RedCanal(
                codigo_inventario=data.get('codigo_inventario'),
                material_construccion=data.get('material_construccion'),
                capacidad_caudal=data.get('capacidad_caudal'),
                longitud_m=length_m,
                ultimo_mantenimiento=data.get('ultimo_mantenimiento'),
                geom=GEOSGeometry(snapped_wkt, srid=25830)
            )
            canal.save()

            return {
                "ok": True,
                "message": f"RedCanal id={canal.id} insertado correctamente.",
                "data": [_geom_to_wkt(canal)]
            }

        except Exception as e:
            return {"ok": False, "message": str(e), "data": None}

    def update(self, data: dict) -> dict:
        """
        Actualiza los campos indicados de un RedCanal existente.

        Parámetros esperados en data:
            id (int) – obligatorio
            + cualquier campo a modificar
        """
        try:
            record_id = data.get('id')
            if not record_id:
                return {"ok": False, "message": "El campo 'id' es obligatorio para actualizar.", "data": None}

            try:
                canal = RedCanal.objects.get(pk=record_id)
            except RedCanal.DoesNotExist:
                return {"ok": False, "message": f"No existe RedCanal con id={record_id}.", "data": None}

            wkt = data.get('geom')
            if wkt:
                snapped_wkt, error = self._snap_and_validate(wkt)
                if error:
                    return {"ok": False, "message": error, "data": None}
                if self._has_intersection(snapped_wkt, exclude_id=record_id):
                    return {
                        "ok": False,
                        "message": "Operación rechazada: la geometría actualizada intersecta con otro canal existente.",
                        "data": None
                    }
                canal.geom = GEOSGeometry(snapped_wkt, srid=25830)
                canal.longitud_m = canal.geom.length
            campos_permitidos = ['codigo_inventario', 'material_construccion', 'capacidad_caudal',
                                'ultimo_mantenimiento', 'geom']
            for field in campos_permitidos:
                if field in data:
                    setattr(canal, field, data[field])

            canal.save()

            return {
                "ok": True,
                "message": f"RedCanal id={canal.id} actualizado correctamente.",
                "data": [_geom_to_wkt(canal)]
            }

        except Exception as e:
            return {"ok": False, "message": str(e), "data": None}

    def delete(self, data: dict) -> dict:
        """
        Elimina un RedCanal por su id.

        Parámetros esperados en data:
            id (int) – obligatorio
        """
        try:
            record_id = data.get('id')
            if not record_id:
                return {"ok": False, "message": "El campo 'id' es obligatorio para eliminar.", "data": None}

            try:
                canal = RedCanal.objects.get(pk=record_id)
            except RedCanal.DoesNotExist:
                return {"ok": False, "message": f"No existe RedCanal con id={record_id}.", "data": None}

            canal.delete()

            return {
                "ok": True,
                "message": f"RedCanal id={record_id} eliminado correctamente.",
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
            qs = RedCanal.objects.all()
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
            qs = RedCanal.objects.all()
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
