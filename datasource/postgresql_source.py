from resources.State import State
import os
import psycopg2
from datetime import datetime
from random import randint

class PostgreSQLDataSource() :
    def open_connection(self) :
        return psycopg2.connect(
            database=os.environ['MAPISTO_DB_NAME'], 
            user=os.environ['MAPISTO_DB_USER'], 
            password=os.environ['MAPISTO_DB_PASSWORD'], 
            host=os.environ['MAPISTO_DB_HOST'], 
            port=os.environ['MAPISTO_DB_PORT'],
            options='-c search_path=mapisto')

    def get_states(self, time:datetime):
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT state_id, color, name, d_path 
        FROM States NATURAL JOIN Territories NATURAL JOIN StateNames 
        WHERE 
            Territories.validity_start <= %s AND Territories.validity_end > %s
            AND  StateNames.validity_start <= %s AND StateNames.validity_end > %s
        ORDER BY state_id
        ''', [time.isoformat()] * 4 )
        records = cursor.fetchall()
        conn.close()
        current_state_id = None
        res = []
        for row in records:
            (state_id, color, name, d_path) = row
            if current_state_id != state_id :
                current_state = State(state_id, name, [d_path], color)
                current_state_id = state_id
                res.append(current_state)
            else :
                current_state.territories.append(d_path)
        return res

    def post_state(self, state:State, validity_start:datetime, validity_end:datetime):
        try:
            conn = self.open_connection()
            with conn.cursor() as curs:
                curs.execute('INSERT INTO States VALUES(default) RETURNING state_id')
                state_id = curs.fetchone()[0]
                for territory_path in state.territories:
                    curs.execute(
                        'INSERT INTO Territories(d_path, precision_in_km, validity_start, validity_end, state_id) VALUES(%s, %s, %s, %s, %s)', 
                        (territory_path, str(1.0), validity_start.isoformat(), validity_end.isoformat(), state_id)
                    )
                curs.execute(
                    'INSERT INTO StateNames(name, state_id, validity_start, validity_end, color) VALUES(%s, %s, %s, %s, %s)',
                    (state.name, state_id, validity_start.isoformat(), validity_end.isoformat(), state.color)
                )
                conn.commit()
                conn.close()
                return state_id
        except Exception as e:
            conn.rollback()
            raise e

