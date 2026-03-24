from psycopg.rows import dict_row
from db.connect import connect
from db.p1Settings import EPSG_CODE

class ZonasConservacion():
    def __init__(self):
        self.conn = connect()
        self.cur = self.conn.cursor()

    def disconnect(self):
        self.cur.close()
        self.conn.close()

    def insert(self, nombre, categoria, entidad, area, fecha_dec, wkt_geom):
        sql = """
        INSERT INTO Eval_01.zonas_conservacion 
            (nombre_area, categoria_proteccion, entidad_responsable, area_hectareas, fecha_declaracion, geom)
        VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s, %s))
        RETURNING id;
        """
        self.cur.execute(sql, [nombre, categoria, entidad, area, fecha_dec, wkt_geom, EPSG_CODE])
        self.conn.commit()
        return self.cur.fetchone()[0]

    def update(self, id_registro, area):
        sql = "UPDATE Eval_01.zonas_conservacion SET area_hectareas = %s WHERE id = %s;"
        self.cur.execute(sql, [area, id_registro])
        self.conn.commit()

    def delete(self, id_registro):
        sql = "DELETE FROM Eval_01.zonas_conservacion WHERE id = %s;"
        self.cur.execute(sql, [id_registro])
        self.conn.commit()

    def selectAsTuples(self):
        self.cur.execute("SELECT id, nombre_area, ST_AsText(geom) FROM Eval_01.zonas_conservacion;")
        return self.cur.fetchall()

    def selectAsDicts(self):
        with self.conn.cursor(row_factory=dict_row) as dcur:
            dcur.execute("SELECT *, ST_AsText(geom) as wkt FROM Eval_01.zonas_conservacion;")
            return dcur.fetchall()