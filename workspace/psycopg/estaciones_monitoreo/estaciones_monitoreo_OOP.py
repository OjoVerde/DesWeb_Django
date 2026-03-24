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

    def insert(self, nombre, tipo, fecha, estado, altitud, wkt_geom):
        sql = """
        INSERT INTO Eval_01.estaciones_monitoreo 
            (nombre, tipo_sensor, fecha_instalacion, estado_operativo, altitud_msnm, geom)
        VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s, %s))
        RETURNING id;
        """
        self.cur.execute(sql, [nombre, tipo, fecha, estado, altitud, wkt_geom, EPSG_CODE])
        self.conn.commit()
        new_id = self.cur.fetchone()[0]
        print(f"Insertado ID: {new_id}")
        return new_id

    def update(self, id_registro, nombre):
        sql = "UPDATE Eval_01.estaciones_monitoreo SET nombre = %s WHERE id = %s;"
        self.cur.execute(sql, [nombre, id_registro])
        self.conn.commit()
        print(f"Registro {id_registro} actualizado.")

    def delete(self, id_registro):
        sql = "DELETE FROM Eval_01.estaciones_monitoreo WHERE id = %s;"
        self.cur.execute(sql, [id_registro])
        self.conn.commit()
        print(f"Registro {id_registro} eliminado.")

    def selectAsTuples(self):
        sql = "SELECT id, nombre, tipo_sensor, ST_AsText(geom) FROM Eval_01.estaciones_monitoreo;"
        self.cur.execute(sql)
        return self.cur.fetchall()

    def selectAsDicts(self):
        with self.conn.cursor(row_factory=dict_row) as dcur:
            sql = "SELECT id, nombre, tipo_sensor, ST_AsText(geom) as wkt FROM Eval_01.estaciones_monitoreo;"
            dcur.execute(sql)
            return dcur.fetchall()