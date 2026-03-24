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

    def insert(self, codigo, material, caudal, longitud, fecha_mant, wkt_geom):
        sql = """
        INSERT INTO Eval_01.red_canales 
            (codigo_inventario, material_construccion, capacidad_caudal, longitud_km, ultima_mantenimiento, geom)
        VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s, %s))
        RETURNING id;
        """
        self.cur.execute(sql, [codigo, material, caudal, longitud, fecha_mant, wkt_geom, EPSG_CODE])
        self.conn.commit()
        return self.cur.fetchone()[0]

    def update(self, id_registro, caudal):
        sql = "UPDATE Eval_01.red_canales SET capacidad_caudal = %s WHERE id = %s;"
        self.cur.execute(sql, [caudal, id_registro])
        self.conn.commit()

    def delete(self, id_registro):
        sql = "DELETE FROM Eval_01.red_canales WHERE id = %s;"
        self.cur.execute(sql, [id_registro])
        self.conn.commit()

    def selectAsTuples(self):
        self.cur.execute("SELECT id, codigo_inventario, ST_AsText(geom) FROM Eval_01.red_canales;")
        return self.cur.fetchall()

    def selectAsDicts(self):
        with self.conn.cursor(row_factory=dict_row) as dcur:
            dcur.execute("SELECT *, ST_AsText(geom) as wkt FROM Eval_01.red_canales;")
            return dcur.fetchall()