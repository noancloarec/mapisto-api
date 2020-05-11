from resources.State import State
from datetime import datetime
from werkzeug.exceptions import NotFound
from resources.StateRepresentation import StateRepresentation
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
