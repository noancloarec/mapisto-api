from resources.Territory import Territory
import psycopg2
from werkzeug.exceptions import NotFound
from resources.BoundingBox import BoundingBox
from resources.MapistoShape import MapistoShape
from datetime import datetime
class TerritoryCRUD:
    @staticmethod
    def add(cursor, territory):
        assert isinstance(territory, Territory)
        try :
            cursor.execute(
                '''
                INSERT INTO territories(state_id, validity_start, validity_end, min_x, max_x, min_y, max_y, name, color) 
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) 
                RETURNING territory_id
                ''',
                (
                    territory.state_id,
                    territory.validity_start.isoformat(),
                    territory.validity_end.isoformat(),
                    territory.bounding_box.x,
                    territory.bounding_box.x + territory.bounding_box.width,
                    territory.bounding_box.y,
                    territory.bounding_box.y + territory.bounding_box.height,
                    territory.name,
                    territory.color
                )
            )
        except psycopg2.Error as e:
            # ForeignKeyViolation 
            if e.pgcode=='23503':
                raise NotFound(f'The state does not exist : {territory.state_id}')
            else:
                raise e
        
        territory_id = cursor.fetchone()[0]
        for shape in territory.representations:
            cursor.execute(
                'INSERT INTO territories_shapes(d_path, precision_in_km, territory_id) VALUES(%s, %s, %s)',
                (
                    shape.d_path,
                    shape.precision_in_km,
                    territory_id
                )
            )
        return territory_id

    
    @staticmethod
    def get(cursor, id):
        cursor.execute('''
            SELECT territories.territory_id, state_id, min_x, min_y, max_x-min_x, max_y-min_y, validity_start, validity_end, color, name, d_path, precision_in_km
            FROM 
                territories INNER JOIN territories_shapes 
                ON territories.territory_id=territories_shapes.territory_id
            WHERE territories.territory_id=%s
            ORDER BY precision_in_km
        ''', (id, ))
        rows = cursor.fetchall()
        if not len(rows):
            raise NotFound(f'Territory not found : {id}')
        (territory_id, state_id, x, y, width, height, validity_start, validity_end, color, name, _, _) = rows[0]
        bounding_box = BoundingBox(x, y, width, height)
        representations = [MapistoShape(row[10], row[11]) for row in rows]
        return Territory(territory_id, representations, state_id, bounding_box, validity_start, validity_end, color, name)

    @staticmethod
    def count(cursor):
        cursor.execute('SELECT COUNT(*) FROM territories')
        return cursor.fetchone()[0]
    

    @staticmethod
    def get_within_bbox_at_time(cursor, bbox, date, precision_level):
        assert isinstance(bbox, BoundingBox)
        assert isinstance(date, datetime)
        cursor.execute('''
            SELECT territories.territory_id, state_id, min_x, min_y, max_x-min_x, max_y-min_y, validity_start, validity_end, color, name, d_path
            FROM 
                territories INNER JOIN territories_shapes 
                ON territories.territory_id=territories_shapes.territory_id
            WHERE 
                territories.validity_start <= %s AND territories.validity_end > %s
                AND precision_in_km=%s
                AND NOT(
                    %s < territories.min_x
                    OR territories.max_x < %s
                    OR %s < territories.min_y
                    OR territories.max_y < %s
                )
        ''', (date, date, precision_level, bbox.max_x, bbox.x, bbox.max_y, bbox.y))
        return [
            Territory(
                territory_id, 
                [MapistoShape(d_path, precision_level)], 
                state_id, 
                BoundingBox(x, y, width, height), 
                validity_start, 
                validity_end, 
                color, 
                name
            )
            for (territory_id, state_id, x, y, width, height, validity_start, validity_end, color, name, d_path) 
            in cursor.fetchall()
            ]

    @staticmethod
    def get_within_bbox_in_period(cursor, bbox, start, end, precision_level):
        assert isinstance(bbox, BoundingBox)
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        cursor.execute('''
            SELECT territories.territory_id, state_id, min_x, min_y, max_x-min_x, max_y-min_y, validity_start, validity_end, color, name, d_path
            FROM 
                territories INNER JOIN territories_shapes 
                ON territories.territory_id=territories_shapes.territory_id
            WHERE 
                territories.validity_start < %s AND territories.validity_end > %s
                AND precision_in_km=%s
                AND NOT(
                    %s < territories.min_x
                    OR territories.max_x < %s
                    OR %s < territories.min_y
                    OR territories.max_y < %s
                )
        ''', (end, start, precision_level, bbox.max_x, bbox.x, bbox.max_y, bbox.y))
        return [
            Territory(
                territory_id, 
                [MapistoShape(d_path, precision_level)], 
                state_id, 
                BoundingBox(x, y, width, height), 
                validity_start, 
                validity_end, 
                color, 
                name
            )
            for (territory_id, state_id, x, y, width, height, validity_start, validity_end, color, name, d_path) 
            in cursor.fetchall()
            ]
