from resources.State import State
from resources.BoundingBox import BoundingBox
from datetime import datetime
from werkzeug.exceptions import NotFound
from resources.StateRepresentation import StateRepresentation
import psycopg2.errors
class StateCRUD:
    @staticmethod
    def add(cursor, state):
        assert isinstance(state, State)
        cursor.execute(
            'INSERT INTO states(validity_start, validity_end) VALUES(%s, %s) RETURNING state_id', 
            (state.validity_start, state.validity_end))
        state_id = cursor.fetchone()[0]
        for rpz in state.representations:
            cursor.execute(
                'INSERT INTO state_names(name, state_id, validity_start, validity_end, color) VALUES(%s, %s, %s, %s, %s)',
                (rpz.name, state_id, rpz.validity_start,
                    rpz.validity_end, rpz.color)
            )
        return state_id
    
    @staticmethod
    def edit(cursor, updated_state):
        assert isinstance(updated_state, State)
        cursor.execute('''
            DELETE FROM state_names
            WHERE state_id=%s
        ''', (updated_state.state_id, ))
        cursor.execute('''
            UPDATE states SET validity_start=%s
            WHERE state_id=%s AND validity_start!=%s
        ''', (updated_state.validity_start, updated_state.state_id, updated_state.validity_start ))
        cursor.execute('''
            UPDATE states SET validity_end=%s
            WHERE state_id=%s AND validity_end!=%s
        ''', (updated_state.validity_end, updated_state.state_id, updated_state.validity_end ))
        for rpz in updated_state.representations:
            try:
                cursor.execute(
                    'INSERT INTO state_names(name, state_id, validity_start, validity_end, color) VALUES(%s, %s, %s, %s, %s)',
                    (rpz.name, updated_state.state_id, rpz.validity_start,
                        rpz.validity_end, rpz.color)
                )
            # Foreign key violation : state_id is not referenced in table states
            except psycopg2.errors.lookup('23503'):
                raise NotFound(f'State does not exist : {updated_state.state_id}')
    @staticmethod
    def count(cursor):
        cursor.execute('''
        SELECT COUNT(*) FROM states
        ''')
        return cursor.fetchone()[0]

    @staticmethod
    def get(cursor, id):
        assert isinstance(id, int)
        cursor.execute('''
            SELECT states.validity_start, states.validity_end,  state_names.name, state_names.validity_start, state_names.validity_end, state_names.color
            FROM states
                INNER JOIN state_names ON state_names.state_id=states.state_id
            WHERE 
                states.state_id=%s 
            ORDER BY state_names.validity_start
        ''', (id, ))
        rows = cursor.fetchall()
        if len(rows)==0:
            raise NotFound(f'State not found : {id}')
        state_start, state_end = rows[0][0] , rows[0][1]
        res = State(id, state_start, state_end, [])
        for row in rows:
            name, start, end, color = row[2], row[3], row[4], row[5]
            res.representations.append(StateRepresentation(name, start, end, color))
        return res

    @staticmethod
    def get_bbox(cursor, id, date):
        assert isinstance(id, int)
        assert isinstance(date, datetime)
        cursor.execute('''
            SELECT MIN(min_x), MIN(min_y), MAX(max_x) , MAX(max_y) 
            FROM territories
            WHERE 
                state_id=%s AND
                validity_start <= %s AND
                validity_end > %s
        ''', (id, date, date))
        row = cursor.fetchone()
        if row[0] is None:
            raise NotFound(f'No map for state {id} at {date.isoformat()} : no territories found at date or non existent state')
        min_x, min_y, max_x, max_y = row
        return BoundingBox(min_x, min_y, max_x-min_x, max_y - min_y)



    @staticmethod
    def get_by_name(cursor, name, validity_start, validity_end):
        assert isinstance(name, str)
        assert isinstance(validity_end, datetime)
        assert isinstance(validity_start, datetime)
        cursor.execute('''
            SELECT state_id 
            FROM state_names
            WHERE 
                validity_start<%s 
                AND validity_end > %s
                AND lower(%s)=lower(name)

            GROUP BY state_id
        ''', (validity_end, validity_start, name))
        ids = [row[0] for row in cursor.fetchall()]
        return [StateCRUD.get(cursor, id) for id in ids]

    # Remove state, names and associated territories
    @staticmethod
    def delete(cursor, state_id):
        assert isinstance(state_id, int)
        cursor.execute('''
            DELETE FROM states WHERE state_id=%s
        ''', (state_id, ))

    @staticmethod
    def search(cursor, pattern):
        assert isinstance(pattern, str)
        cursor.execute('''
                SELECT state_id
                FROM state_names
                WHERE
                    name != '' AND
                    (
                        lower(name) LIKE(CONCAT('%%', lower(%s), '%%')) 
                        OR lower(%s) LIKE (CONCAT('%%', lower(name), '%%'))
                    )
                GROUP BY state_id
                LIMIT 20
        ''', (pattern, pattern))
        matching_state_ids = [row[0] for row in cursor.fetchall()]
        for stid in matching_state_ids:
            assert isinstance(stid, int)
        return StateCRUD.get_many(cursor, matching_state_ids)

    @staticmethod
    def get_many(cursor, state_ids):
        if len(state_ids)==0:
            return []
        cursor.execute('''
            SELECT 
                states.state_id, states.validity_start, states.validity_end,  
                state_names.name, state_names.validity_start, state_names.validity_end, state_names.color
            FROM states
                INNER JOIN state_names ON state_names.state_id=states.state_id
            WHERE 
                states.state_id IN %s 
            ORDER BY states.state_id,  state_names.validity_start

        ''', (tuple(state_ids),))
        records = cursor.fetchall()
        current_state_id = None
        res = []
        for row in records:
            (state_id, validity_start, validity_end, name, name_validity_start, name_validity_end, color) = row
            representation = StateRepresentation(name, name_validity_start, name_validity_end, color)
            if current_state_id != state_id:
                current_state = State(state_id,
                                      validity_start=validity_start,
                                      validity_end=validity_end,
                                      representations = [representation]
                                      )
                current_state_id = state_id
                res.append(current_state)
            else:
                current_state.representations.append(representation)
        return res

