from psycopg.rows import dict_row
from db.connect import connect
from db.p1Settings import EPSG_CODE

class EstacionesMonitoreo():

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

    def _is_within_zona(self, snapped_wkt):
        """True si el punto está estrictamente dentro de alguna zona de conservación."""
        sql = """
            SELECT EXISTS(
                SELECT 1 FROM zonas_conservacion
                WHERE ST_Within(ST_GeomFromText(%s, %s), geom)
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
            'nombre', 'tipo_sensor', 'fecha_instalacion',
            'estado_operativo', 'altitud_msnm', 'geom'  (WKT Point)
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

            if not self._is_within_zona(snapped_wkt):
                return {
                    "ok": False,
                    "message": "El punto no se encuentra dentro de ninguna zona de conservación (ST_Within). Operación rechazada.",
                    "data": None
                }

            sql = """
                INSERT INTO estaciones_monitoreo
                    (nombre, tipo_sensor, fecha_instalacion,
                     estado_operativo, altitud_msnm, geom)
                VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s, %s))
                RETURNING id;
            """
            self.cur.execute(sql, [
                params.get('nombre'),
                params.get('tipo_sensor'),
                params.get('fecha_instalacion'),
                params.get('estado_operativo', True),
                params.get('altitud_msnm'),
                snapped_wkt,
                EPSG_CODE
            ])
            self.conn.commit()
            new_id = self.cur.fetchone()[0]
            return {
                "ok": True,
                "message": f"Estación de monitoreo insertada correctamente con ID {new_id}.",
                "data": [{"id": new_id}]
            }
        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "message": f"Error en insert: {e}", "data": None}

    def update(self, params: dict) -> dict:
        """
        params: {
            'id',
            y cualquier combinación de: 'nombre', 'tipo_sensor', 'fecha_instalacion',
            'estado_operativo', 'altitud_msnm', 'geom'
        }
        """
        try:
            record_id = params['id']
            updatable = {
                'nombre', 'tipo_sensor', 'fecha_instalacion',
                'estado_operativo', 'altitud_msnm'
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
                if not self._is_within_zona(snapped_wkt):
                    return {
                        "ok": False,
                        "message": "El punto actualizado no se encuentra dentro de ninguna zona de conservación (ST_Within). Operación rechazada.",
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
            sql = f"UPDATE estaciones_monitoreo SET {', '.join(set_clauses)} WHERE id = %s RETURNING id;"

            self.cur.execute(sql, values)
            self.conn.commit()
            updated = self.cur.fetchone()
            if updated is None:
                return {"ok": False, "message": f"No existe registro con id={record_id}.", "data": None}
            return {
                "ok": True,
                "message": f"Estación ID {record_id} actualizada correctamente.",
                "data": [{"id": updated[0]}]
            }
        except Exception as e:
            self.conn.rollback()
            return {"ok": False, "message": f"Error en update: {e}", "data": None}

    def delete(self, params: dict) -> dict:
        """params: {'id': <int>}"""
        try:
            record_id = params['id']
            sql = "DELETE FROM estaciones_monitoreo WHERE id = %s RETURNING id;"
            self.cur.execute(sql, [record_id])
            self.conn.commit()
            deleted = self.cur.fetchone()
            if deleted is None:
                return {"ok": False, "message": f"No existe registro con id={record_id}.", "data": None}
            return {
                "ok": True,
                "message": f"Estación ID {record_id} eliminada correctamente.",
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
                    SELECT id, nombre, tipo_sensor, fecha_instalacion,
                           estado_operativo, altitud_msnm, ST_AsText(geom) AS wkt
                    FROM estaciones_monitoreo WHERE id = %s;
                """
                self.cur.execute(sql, [params['id']])
            else:
                sql = """
                    SELECT id, nombre, tipo_sensor, fecha_instalacion,
                           estado_operativo, altitud_msnm, ST_AsText(geom) AS wkt
                    FROM estaciones_monitoreo;
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
                        SELECT id, nombre, tipo_sensor, fecha_instalacion,
                               estado_operativo, altitud_msnm, ST_AsText(geom) AS wkt
                        FROM estaciones_monitoreo WHERE id = %s;
                    """
                    dcur.execute(sql, [params['id']])
                else:
                    sql = """
                        SELECT id, nombre, tipo_sensor, fecha_instalacion,
                               estado_operativo, altitud_msnm, ST_AsText(geom) AS wkt
                        FROM estaciones_monitoreo;
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