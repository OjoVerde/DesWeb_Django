from psycopg.rows import dict_row
from db.connect import connect
from db.p1Settings import EPSG_CODE

class RedCanales():

    def __init__(self):
        self.conn = connect()
        self.cur = self.conn.cursor()

    def disconnect(self):
        self.cur.close()
        self.conn.close()

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _snap_and_validate(self, wkt_geom):
        """Devuelve (snapped_wkt, is_valid). Lanza excepción si la WKT es inválida."""
        sql = """
            SELECT
                ST_AsText(ST_SnapToGrid(ST_GeomFromText(%s, %s), 0.0001)) AS snapped_wkt,
                ST_IsValid(ST_SnapToGrid(ST_GeomFromText(%s, %s), 0.0001))  AS is_valid
        """
        self.cur.execute(sql, [wkt_geom, EPSG_CODE, wkt_geom, EPSG_CODE])
        row = self.cur.fetchone()
        return row[0], row[1]

    def _has_intersection(self, snapped_wkt, exclude_id=None):
        """True si la geometría intersecta con algún canal ya existente."""
        if exclude_id is not None:
            sql = """
                SELECT EXISTS(
                    SELECT 1 FROM red_canales
                    WHERE ST_Intersects(geom, ST_GeomFromText(%s, %s))
                      AND id != %s
                )
            """
            self.cur.execute(sql, [snapped_wkt, EPSG_CODE, exclude_id])
        else:
            sql = """
                SELECT EXISTS(
                    SELECT 1 FROM red_canales
                    WHERE ST_Intersects(geom, ST_GeomFromText(%s, %s))
                )
            """
            self.cur.execute(sql, [snapped_wkt, EPSG_CODE])
        return self.cur.fetchone()[0]

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def insert(self, params: dict) -> dict:
        """
        params: {
            'codigo_inventario', 'material_construccion', 'capacidad_caudal',
            'longitud_m', 'ultimo_mantenimiento', 'geom'  (WKT LineString)
        }
        """
        try:
            wkt_geom = params['geom']

            snapped_wkt, is_valid = self._snap_and_validate(wkt_geom)
            if not is_valid:
                return {
                    "ok": False,
                    "message": "Geometría inválida según ST_IsValid. Operación rechazada.",
                    "data": None
                }

            if self._has_intersection(snapped_wkt):
                return {
                    "ok": False,
                    "message": "La geometría intersecta con un canal existente. Operación rechazada.",
                    "data": None
                }

            sql = """
                INSERT INTO red_canales
                    (codigo_inventario, material_construccion, capacidad_caudal,
                     longitud_m, ultimo_mantenimiento, geom)
                VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s, %s))
                RETURNING id;
            """
            self.cur.execute(sql, [
                params.get('codigo_inventario'),
                params.get('material_construccion'),
                params.get('capacidad_caudal'),
                params.get('longitud_m'),
                params.get('ultimo_mantenimiento'),
                snapped_wkt,
                EPSG_CODE
            ])
            self.conn.commit()
            new_id = self.cur.fetchone()[0]
            return {
                "ok": True,
                "message": f"Canal insertado correctamente con ID {new_id}.",
                "data": [{"id": new_id}]
            }
        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "message": f"Error en insert: {e}", "data": None}

    def update(self, params: dict) -> dict:
        """
        params: {
            'id',
            y cualquier combinación de: 'codigo_inventario', 'material_construccion',
            'capacidad_caudal', 'longitud_m', 'ultimo_mantenimiento', 'geom'
        }
        """
        try:
            record_id = params['id']
            updatable = {
                'codigo_inventario', 'material_construccion', 'capacidad_caudal',
                'longitud_m', 'ultimo_mantenimiento'
            }
            fields = {k: v for k, v in params.items() if k in updatable}
            snapped_wkt = None

            if 'geom' in params:
                snapped_wkt, is_valid = self._snap_and_validate(params['geom'])
                if not is_valid:
                    return {
                        "ok": False,
                        "message": "Geometría inválida según ST_IsValid. Operación rechazada.",
                        "data": None
                    }
                if self._has_intersection(snapped_wkt, exclude_id=record_id):
                    return {
                        "ok": False,
                        "message": "La geometría actualizada intersecta con otro canal existente. Operación rechazada.",
                        "data": None
                    }

            if not fields and snapped_wkt is None:
                return {
                    "ok": False,
                    "message": "No se proporcionaron campos para actualizar.",
                    "data": None
                }

            set_clauses = [f"{col} = %s" for col in fields]
            values = list(fields.values())

            if snapped_wkt is not None:
                set_clauses.append("geom = ST_GeomFromText(%s, %s)")
                values += [snapped_wkt, EPSG_CODE]

            values.append(record_id)
            sql = f"UPDATE red_canales SET {', '.join(set_clauses)} WHERE id = %s RETURNING id;"

            self.cur.execute(sql, values)
            self.conn.commit()
            updated = self.cur.fetchone()
            if updated is None:
                return {"ok": False, "message": f"No existe registro con id={record_id}.", "data": None}
            return {
                "ok": True,
                "message": f"Canal ID {record_id} actualizado correctamente.",
                "data": [{"id": updated[0]}]
            }
        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "message": f"Error en update: {e}", "data": None}

    def delete(self, params: dict) -> dict:
        """params: {'id': <int>}"""
        try:
            record_id = params['id']
            sql = "DELETE FROM red_canales WHERE id = %s RETURNING id;"
            self.cur.execute(sql, [record_id])
            self.conn.commit()
            deleted = self.cur.fetchone()
            if deleted is None:
                return {"ok": False, "message": f"No existe registro con id={record_id}.", "data": None}
            return {
                "ok": True,
                "message": f"Canal ID {record_id} eliminado correctamente.",
                "data": [{"id": deleted[0]}]
            }
        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "message": f"Error en delete: {e}", "data": None}

    def selectAsTuples(self, params: dict = {}) -> dict:
        """params: {} para todos, o {'id': <int>} para filtrar por id."""
        try:
            if 'id' in params:
                sql = """
                    SELECT id, codigo_inventario, material_construccion, capacidad_caudal,
                           longitud_m, ultimo_mantenimiento, ST_AsText(geom) AS wkt
                    FROM red_canales WHERE id = %s;
                """
                self.cur.execute(sql, [params['id']])
            else:
                sql = """
                    SELECT id, codigo_inventario, material_construccion, capacidad_caudal,
                           longitud_m, ultimo_mantenimiento, ST_AsText(geom) AS wkt
                    FROM red_canales;
                """
                self.cur.execute(sql)
            rows = self.cur.fetchall()
            return {
                "ok": True,
                "message": f"{len(rows)} registro(s) encontrado(s).",
                "data": rows
            }
        except Exception as e:
            return {"ok": False, "message": f"Error en selectAsTuples: {e}", "data": None}

    def selectAsDicts(self, params: dict = {}) -> dict:
        """params: {} para todos, o {'id': <int>} para filtrar por id."""
        try:
            with self.conn.cursor(row_factory=dict_row) as dcur:
                if 'id' in params:
                    sql = """
                        SELECT id, codigo_inventario, material_construccion, capacidad_caudal,
                               longitud_m, ultimo_mantenimiento, ST_AsText(geom) AS wkt
                        FROM red_canales WHERE id = %s;
                    """
                    dcur.execute(sql, [params['id']])
                else:
                    sql = """
                        SELECT id, codigo_inventario, material_construccion, capacidad_caudal,
                               longitud_m, ultimo_mantenimiento, ST_AsText(geom) AS wkt
                        FROM red_canales;
                    """
                    dcur.execute(sql)
                rows = dcur.fetchall()
            return {
                "ok": True,
                "message": f"{len(rows)} registro(s) encontrado(s).",
                "data": rows
            }
        except Exception as e:
            return {"ok": False, "message": f"Error en selectAsDicts: {e}", "data": None}