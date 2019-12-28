from resources.State import State
import os
import psycopg2
from datetime import datetime
from random import randint
from resources.Territory import Territory
from resources.TerritoryShape import TerritoryShape

class PostgreSQLDataSource() :
    def open_connection(self) :
        return psycopg2.connect(
            database=os.environ['MAPISTO_DB_NAME'], 
            user=os.environ['MAPISTO_DB_USER'], 
            password=os.environ['MAPISTO_DB_PASSWORD'], 
            host=os.environ['MAPISTO_DB_HOST'], 
            port=os.environ['MAPISTO_DB_PORT'],
            options='-c search_path=mapisto')

    def get_states(self, time:datetime, precision:float, bbmin_x, bbmax_x, bbmin_y, bbmax_y):
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT state_id, color, name, d_path, territory_id
        FROM states NATURAL JOIN territories NATURAL JOIN state_names NATURAL JOIN territories_shapes 
        WHERE 
            territories.validity_start <= %s AND territories.validity_end > %s
            AND  state_names.validity_start <= %s AND state_names.validity_end > %s
            AND precision_in_km=%s
            AND NOT(
                %s < territories.min_x
                OR territories.max_x < %s
                OR %s < territories.min_y
                OR territories.max_y < %s
            )
        ORDER BY state_id
        ''', [time.isoformat()] * 4 + [precision, bbmax_x, bbmin_x, bbmax_y, bbmin_y])
        records = cursor.fetchall()
        conn.close()
        current_state_id = None
        res = []
        for row in records:
            (state_id, color, name, d_path, territory_id) = row
            if current_state_id != state_id :
                current_state = State(state_id, name, [Territory(territory_id, representations=[TerritoryShape(d_path)])], color)
                current_state_id = state_id
                res.append(current_state)
            else :
                current_state.territories.append(d_path)
        return res

    def add_state(self, state:State, validity_start:datetime, validity_end:datetime):
        try:
            conn = self.open_connection()
            with conn.cursor() as curs:
                curs.execute('INSERT INTO states VALUES(default) RETURNING state_id')
                state_id = curs.fetchone()[0]
                curs.execute(
                    'INSERT INTO state_names(name, state_id, validity_start, validity_end, color) VALUES(%s, %s, %s, %s, %s)',
                    (state.name, state_id, validity_start.isoformat(), validity_end.isoformat(), state.color)
                )
                for territory in state.territories:
                    curs.execute(
                        'INSERT INTO territories(state_id, validity_start, validity_end, min_x, max_x, min_y, max_y) VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING territory_id', 
                        (
                            state_id,
                            validity_start.isoformat(), 
                            validity_end.isoformat(), 
                            territory.min_x, 
                            territory.max_x, 
                            territory.min_y,
                            territory.max_y
                        )
                    )
                    territory_id = curs.fetchone()[0]
                    for territory_shape in territory.representations:
                        curs.execute(
                            'INSERT INTO territories_shapes(d_path, precision_in_km, territory_id) VALUES(%s, %s, %s)',
                            (
                                territory_shape.d_path,
                                territory_shape.precision_in_km,
                                territory_id
                            )
                        )
                conn.commit()
                conn.close()
                return state_id
        except Exception as e:
            conn.rollback()
            raise e
    
    def get_land(self):
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT d_path 
        FROM LandMasses;
        ''')
        records = cursor.fetchall()
        conn.close()
        return [tup[0] for tup in records]

