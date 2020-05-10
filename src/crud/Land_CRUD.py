import conf
import psycopg2
from werkzeug.exceptions import NotFound
from resources.Land import Land
from resources.BoundingBox import BoundingBox
from resources.MapistoShape import MapistoShape
class LandCRUD:
    @staticmethod
    def get_land(cursor, land_id):
        assert isinstance(land_id, int)
        cursor.execute('''
                SELECT min_x, max_x, min_y, max_y, d_path, precision_in_km
        FROM lands NATURAL JOIN lands_shapes 
        WHERE 
            land_id=%s
        ''', (land_id , ))
        rows = cursor.fetchall()
        if not len(rows):
            raise NotFound(f"Cannot find land no {land_id}")        
        (minx, maxx, miny, maxy,_, _) = rows[0]
        res = Land(land_id, [], BoundingBox(minx, miny, maxx-minx, maxy-miny))
        for row in rows:
            (_,_,_,_, d_path, precision) = row
            res.representations.append(MapistoShape(d_path, precision))
        return res
    
    @staticmethod
    def count(cursor):
        cursor.execute('SELECT COUNT(*) from lands')
        return cursor.fetchone()[0]

    @staticmethod
    def add_land(cursor, land):
        assert isinstance(land, Land)
        assert len(land.representations) > 0
        cursor.execute(
            'INSERT INTO lands(min_x, max_x, min_y, max_y) VALUES(%s, %s, %s, %s) RETURNING land_id',
            (
                land.bounding_box.x,
                land.bounding_box.x + land.bounding_box.width,
                land.bounding_box.y,
                land.bounding_box.y + land.bounding_box.height
            )
        )
        land_id = cursor.fetchone()[0]
        for land_shape in land.representations:
            cursor.execute(
                'INSERT INTO lands_shapes(d_path, precision_in_km, land_id) VALUES(%s, %s, %s)',
                (
                    land_shape.d_path,
                    land_shape.precision_in_km,
                    land_id
                )
            )
        return land_id
