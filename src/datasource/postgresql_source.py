from resources.State import State
import os
import psycopg2
from datetime import datetime
from random import randint
from resources.Territory import Territory
from resources.TerritoryShape import TerritoryShape
from resources.Land import Land
from resources.LandShape import LandShape
from resources.BoundingBox import BoundingBox
import logging
from werkzeug.exceptions import InternalServerError, NotFound, BadRequest
from maps_geometry.compression import path_contains_point
import pytz


class PostgreSQLDataSource():
    def open_connection(self):
        return psycopg2.connect(
            database=os.environ['MAPISTO_DB_NAME'],
            user=os.environ['MAPISTO_DB_USER'],
            password=os.environ['MAPISTO_DB_PASSWORD'],
            host=os.environ['MAPISTO_DB_HOST'],
            port=os.environ['MAPISTO_DB_PORT'],
            options='-c search_path=mapisto')

    def get_states(self, time: datetime, precision: float, bbmin_x, bbmax_x, bbmin_y, bbmax_y):
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT 
            states.state_id, 
            color,
            name,
            d_path,
            territory_id,
            state_names.validity_start,
            state_names.validity_end,
            territories.validity_start,
            territories.validity_end,
            territories.min_x,
            territories.max_x,
            territories.min_y,
            territories.max_y
        FROM states 
            INNER  JOIN territories ON states.state_id=territories.state_id 
            INNER JOIN state_names ON state_names.state_id=states.state_id 
            NATURAL JOIN territories_shapes 
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
            (state_id, color, name, d_path, territory_id, state_validity_start,
             state_validity_end, territory_validity_start, territory_validity_end,
             min_x, max_x, min_y, max_y) = row
            territory = Territory(
                territory_id,
                representations=[TerritoryShape(d_path)],
                validity_start=territory_validity_start,
                validity_end=territory_validity_end,
                bounding_box=BoundingBox(min_x, min_y, max_x-min_x, max_y-min_y)
            )
            if current_state_id != state_id:
                current_state = State(state_id, name, [territory], color,
                                      validity_start=state_validity_start,
                                      validity_end=state_validity_end
                                      )
                current_state_id = state_id
                res.append(current_state)
            else:
                current_state.territories.append(territory)
        return res

    def get_state(self, state_id: int, time: datetime, precision: int):
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT states.state_id, color, name, state_names.validity_start, state_names.validity_end, MIN(min_x), MIN(min_y), MAX(max_x), MAX(max_y)
        FROM states
            INNER  JOIN territories ON states.state_id=territories.state_id
            INNER JOIN state_names ON state_names.state_id=states.state_id
            NATURAL JOIN territories_shapes
        WHERE 
            states.state_id=%s 
            AND
            territories.validity_start <= %s AND territories.validity_end > %s
            AND  state_names.validity_start <= %s AND state_names.validity_end > %s
            AND precision_in_km=%s
        GROUP BY states.state_id, color, state_names.name, state_names.validity_start, state_names.validity_end
        ''', [state_id] + [time.isoformat()] * 4 + [precision])
        records = cursor.fetchall()
        conn.close()
        if len(records) > 1:
            raise InternalServerError(
                "Several state names found for 1 id and time. Maybe 2 state_names overlap in time")
        if len(records) == 0:
            raise NotFound(
                f"State no {state_id} not found on the {time.isoformat()} ")
        (state_id, color, name, validity_start, validity_end,
         min_x, min_y, max_x, max_y) = records[0]
        bbox = BoundingBox(min_x, min_y, max_x-min_x, max_y-min_y)
        return State(state_id, name, color=color, validity_start=validity_start, validity_end=validity_end, bounding_box=bbox)

    def get_state_from_territory(self, territory_id: int, time: datetime):
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT states.state_id, state_names.name, state_names.validity_start, state_names.validity_end, state_names.color
        FROM states 
            INNER  JOIN territories ON states.state_id=territories.state_id 
            INNER JOIN state_names ON state_names.state_id=states.state_id 
        WHERE 
            territories.territory_id = %s 
            AND  state_names.validity_start <= %s AND state_names.validity_end > %s
        ''', [territory_id, time.isoformat(), time.isoformat()])
        records = cursor.fetchall()
        conn.close()
        if len(records) > 1:
            raise InternalServerError(
                "Several state names found for 1 territory and 1 time. Maybe 2 state_names overlap in time")
        if len(records) == 0:
            raise NotFound(
                "Territory does not exist or does not have a state representation at this time")
        (state_id, name, validity_start, validity_end, color) = records[0]
        return State(state_id, name, color=color, validity_start=validity_start, validity_end=validity_end)

    def add_state(self, state: State, validity_start: datetime, validity_end: datetime):
        try:
            conn = self.open_connection()
            with conn.cursor() as curs:
                curs.execute(
                    'INSERT INTO states VALUES(default) RETURNING state_id')
                state_id = curs.fetchone()[0]
                curs.execute(
                    'INSERT INTO state_names(name, state_id, validity_start, validity_end, color) VALUES(%s, %s, %s, %s, %s)',
                    (state.name, state_id, validity_start.isoformat(),
                     validity_end.isoformat(), state.color)
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

    def edit_state(self, state: State, validity_start, validity_end):
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE state_names SET name=%s, color=%s
            WHERE state_id=%s AND validity_start = %s AND validity_end=%s
        ''', (state.name, state.color, state.state_id, validity_start.isoformat(), validity_end.isoformat()))
        rowcount = cursor.rowcount
        conn.commit()
        cursor.close()
        if rowcount == 1:
            return state.state_id
        elif rowcount > 1:
            raise InternalServerError(
                f"Several tuples found for ({state.state_id}, {validity_start.isoformat()} ,  {validity_end.isoformat()})")
        else:
            raise NotFound(
                f"No state found for ({state.state_id}, {validity_start.isoformat()} ,  {validity_end.isoformat()})")

    def get_land(self, precision: float, bbmin_x, bbmax_x, bbmin_y, bbmax_y):
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT land_id, d_path
        FROM lands NATURAL JOIN lands_shapes 
        WHERE 
            precision_in_km=%s
            AND NOT(
                %s < lands.min_x
                OR lands.max_x < %s
                OR %s < lands.min_y
                OR lands.max_y < %s
            )
        ''',
                       (precision, bbmax_x, bbmin_x, bbmax_y, bbmin_y)
                       )
        records = cursor.fetchall()
        conn.close()
        return [Land(row[0], [LandShape(row[1])]) for row in records]

    def add_land(self, land: Land):
        try:
            conn = self.open_connection()
            with conn.cursor() as curs:
                curs.execute(
                    'INSERT INTO lands(min_x, max_x, min_y, max_y) VALUES(%s, %s, %s, %s) RETURNING land_id',
                    (
                        land.min_x,
                        land.max_x,
                        land.min_y,
                        land.max_y
                    )
                )
                land_id = curs.fetchone()[0]
                for land_shape in land.representations:
                    curs.execute(
                        'INSERT INTO lands_shapes(d_path, precision_in_km, land_id) VALUES(%s, %s, %s)',
                        (
                            land_shape.d_path,
                            land_shape.precision_in_km,
                            land_id
                        )
                    )
                conn.commit()
                conn.close()
                return land_id
        except Exception as e:
            conn.rollback()
            raise e

    def check_extend_request_validity(self, to_extend: int, newStart: datetime, newEnd: datetime):
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, validity_start, validity_end FROM state_names 
            WHERE 
            state_id=%s 
            AND validity_start < %s
            AND validity_end > %s
        ''',
                       (to_extend, newEnd, newStart)
                       )
        records = cursor.fetchall()
        if len(records) > 1:
            raise InternalServerError(
                f"Several state_names were found for {to_extend}({records[0][0]}) : {str(records)}")
        elif not len(records):
            raise NotFound(
                f"State no {to_extend} has no representations between {str(newStart)} and {str(newEnd)}")
        else:
            name, validity_start, validity_end = records[0]
            if validity_start.replace(tzinfo=pytz.UTC) < newStart or validity_end.replace(tzinfo=pytz.UTC) > newEnd:
                raise BadRequest(
                    f"The state you try to extend has a period ({validity_start}, {validity_end}) out of the the extended period you provide ({newStart}, {newEnd})")
            return name
        conn.close()

    def get_concurrent_states(self, to_extend: int, newStart: datetime, newEnd: datetime):
        to_extend_name = self.check_extend_request_validity(
            to_extend, newStart, newEnd)
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT state_id, name, validity_start, validity_end FROM state_names 
            WHERE 
            name!='' 
            AND state_id !=%s
            AND validity_start < %s
            AND validity_end > %s
            AND (
                lower(name) LIKE(CONCAT('%%', lower(%s), '%%')) 
                OR lower(%s) LIKE (CONCAT('%%', lower(name), '%%'))
                )
        ''',
                       (to_extend, newEnd, newStart,
                        to_extend_name, to_extend_name)
                       )
        records = cursor.fetchall()
        conn.close()
        return [State(row[0], name=row[1], validity_start=row[2], validity_end=row[3]) for row in records]

    def get_mandatory_merged_states(self, to_extend_id:int, to_extend_name: str, newStart: datetime, newEnd: datetime):
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT state_id, name, validity_start, validity_end FROM state_names 
            WHERE 
            state_id!=%s
            AND lower(name) = lower(%s)
            AND validity_start < %s
            AND validity_end > %s
        ''',
                       (to_extend_id ,to_extend_name, newEnd, newStart)
                       )
        records = cursor.fetchall()
        conn.close()
        return [State(row[0], name=row[1], validity_start=row[2], validity_end=row[3]) for row in records]

    def state_is_within_period(self, state: State, start: datetime, end: datetime):
        return state.validity_start.replace(tzinfo=pytz.UTC) >= start and state.validity_end.replace(tzinfo=pytz.UTC) <= end

    def get_states_by_period(self, state_ids, start: datetime, end: datetime):
        conn = self.open_connection()
        cursor = conn.cursor()
        logging.info(state_ids)
        cursor.execute('''
            SELECT state_id, name, validity_start, validity_end FROM state_names 
            WHERE 
            state_id IN %s
            AND validity_start < %s
            AND validity_end > %s
        ''',
                       (tuple(state_ids), end, start)
                       )
        records = cursor.fetchall()
        conn.close()
        return [State(row[0], name=row[1], validity_start=row[2], validity_end=row[3]) for row in records]

    def extend_state(self, to_extend: int, newStart: datetime, newEnd: datetime, to_be_merged: list):
        to_extend_name = self.check_extend_request_validity(
            to_extend, newStart, newEnd)
        to_reassign_mandatory = self.get_mandatory_merged_states(to_extend,
            to_extend_name, newStart, newEnd)
        mandatory_out_of_bounds = [
            s for s in to_reassign_mandatory if not self.state_is_within_period(s, newStart, newEnd)]
        if len(mandatory_out_of_bounds):
            raise BadRequest(
                f"Cannot extend : These states conflict because they have the same name and overlap with your extend period : {[str(s) for s in mandatory_out_of_bounds]}")
        to_be_merged_optional = [state_id for state_id in to_be_merged if state_id not in map(lambda s:s.state_id, to_reassign_mandatory) ]
        if len(to_be_merged_optional):
            to_reassign_optional = self.get_states_by_period(to_be_merged, newStart, newEnd)
            state_to_merge_not_found = [state_id for state_id in to_be_merged_optional if state_id not in map(lambda s: s.state_id, to_reassign_optional)]
            if state_to_merge_not_found:
                raise NotFound(f"Could not find the states to merge them : {state_to_merge_not_found} ")
            logging.info(f"Optional found : {[str(s) for s in to_reassign_optional]}")
            optional_out_of_bounds = [
                s for s in to_reassign_optional if not self.state_is_within_period(s, newStart, newEnd)]
            if len(optional_out_of_bounds):
                raise BadRequest(
                    f"Cannot extend : These states conflict because they overlap with your extend period : {[str(s) for s in optional_out_of_bounds]}")
        else:
            to_reassign_optional = []
        # Actually performs the edit
        try:
            conn = self.open_connection()
            with conn.cursor() as curs:
                for to_reassign in to_reassign_mandatory + to_reassign_optional:
                    logging.info(f"About to remove state {to_reassign}")
                    curs.execute(
                        """
                        UPDATE territories 
                        SET state_id=%s
                        WHERE 
                        state_id=%s
                        AND validity_start>= %s
                        AND validity_end <= %s
                        """,
                        (
                            to_extend,
                            to_reassign.state_id,
                            to_reassign.validity_start,
                            to_reassign.validity_end
                        )
                    )
                    curs.execute(
                        """
                        DELETE FROM state_names 
                        WHERE 
                        state_id = %s
                        AND validity_start=%s
                        AND validity_end=%s
                        """ , (to_reassign.state_id, to_reassign.validity_start, to_reassign.validity_end)
                    )
                    curs.execute('DELETE FROM states WHERE state_id=%s', (to_reassign.state_id,))
                curs.execute("""
                    UPDATE state_names
                    SET validity_start=%s, validity_end=%s 
                    WHERE 
                        state_id=%s
                        AND validity_start>=%s
                        AND validity_end<=%s
                """, (newStart, newEnd, to_extend, newStart, newEnd))
                conn.commit()
                conn.close()
                return { "removed_states" : to_reassign_mandatory+to_reassign_optional}
        except Exception as e:
            conn.rollback()
            logging.warning("Canceled transaction")
            raise e

    def get_concurrent_territories(self, territory_id, newStart, newEnd, capital_x, capital_y, precision):
        self.check_territories_exist_within([territory_id], newStart, newEnd)
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT territory_id, min_x, max_x, min_y, max_y, validity_start, validity_end, d_path, state_id
            FROM territories NATURAL JOIN territories_shapes 
            WHERE
             territory_id!=%s
             AND precision_in_km=%s 
             AND min_x <= %s 
             AND max_x >= %s 
             AND min_y <= %s 
             AND max_y >= %s 
             AND validity_start < %s
             AND validity_end > %s
             ORDER BY validity_start
            ''',
                       (territory_id, precision, capital_x, capital_x, capital_y, capital_y,
                        newEnd, newStart)
                       )
        records = cursor.fetchall()
        conn.close()
        territories = []
        for row in records :
            terr_id, min_x, max_x, min_y, max_y, validity_start, validity_end, d_path, state_id = row
            territories.append(Territory(
                terr_id, 
                [TerritoryShape(d_path)] , 
                BoundingBox(min_x, 
                min_y, 
                max_x-min_x, 
                max_y-min_y), 
                validity_start, 
                validity_end,
                state_id=state_id
                ))

        # Filter out the territories which do not contain the capital
        territories = [territory for territory in territories if path_contains_point(territory.representations[0].d_path , (capital_x, capital_y))]

        # Removes the d_path data to alleviate the json response
        for territory in territories:
            territory.representations = None
        
        return territories
    
    def check_territories_exist_within(self, territory_ids, newStart, newEnd) :
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT territory_id
            FROM territories
            WHERE territory_id IN %s
            AND validity_start >= %s
            AND validity_end <= %s
        ''', (tuple(territory_ids), newStart, newEnd))
        terr_id_retrieved = list(map(lambda row : row[0] , cursor.fetchall()))
        conn.close()
        if len(terr_id_retrieved) != len(territory_ids):
            raise NotFound(f"Territories no {[terr_id for terr_id in territory_ids if terr_id not in terr_id_retrieved]} do not exist within ({newStart.isoformat(), newEnd.isoformat()}) ")        

    def extend_territory(self, to_extend: int, newStart: datetime, newEnd: datetime, to_be_removed: list):
        self.check_territories_exist_within([to_extend]+to_be_removed, newStart, newEnd)
        try:
            conn = self.open_connection()
            with conn.cursor() as curs:
                curs.execute("""
                    UPDATE territories
                    SET validity_start=%s, validity_end=%s 
                    WHERE 
                        territory_id=%s
                """, (newStart, newEnd, to_extend))
                if len(to_be_removed) :
                    curs.execute("""
                        DELETE FROM Territories_shapes
                        WHERE territory_id IN %s
                    """, (tuple(to_be_removed),))
                    curs.execute("""
                        DELETE FROM Territories
                        WHERE territory_id in %s
                    """, (tuple(to_be_removed),))
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            conn.rollback()
            logging.warning("Canceled transaction")
            raise e
    def get_territory(self, territory_id):
        conn = self.open_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT territory_id, validity_start, validity_end, min_x, min_y, max_x, max_y, state_id
            FROM territories
            WHERE territory_id = %s
        ''', (territory_id ,))
        territory_id, validity_start, validity_end, min_x, min_y, max_x, max_y, state_id = cursor.fetchone()
        conn.close()
        return Territory(territory_id, [], BoundingBox(min_x, min_y, max_x-min_x, max_y-min_y), validity_start, validity_end, state_id)
    
    def search_states(self, pattern, start=None, end=None):
        conn=self.open_connection()
        cursor=conn.cursor()
        if start and end :
            cursor.execute(
                '''
                SELECT state_id, name, color, validity_start, validity_end 
                FROM state_names
                WHERE
                    name != ''
                    AND validity_start <= %s 
                    AND validity_end >= %s
                    AND
                    (
                    lower(name) LIKE(CONCAT('%%', lower(%s), '%%')) 
                    OR lower(%s) LIKE (CONCAT('%%', lower(name), '%%'))
                    )
                LIMIT 20
                ''',
                (start, end, pattern, pattern)
            )
        else:
            cursor.execute(
                '''
                SELECT state_id, name, color, validity_start, validity_end 
                FROM state_names
                WHERE
                    name != '' AND
                    (
                        lower(name) LIKE(CONCAT('%%', lower(%s), '%%')) 
                        OR lower(%s) LIKE (CONCAT('%%', lower(name), '%%'))
                    )
                LIMIT 20
                ''',
                (pattern, pattern)
            )
        res = []
        for row in cursor.fetchall():
            (state_id, name, color, validity_start, validity_end) = row
            res.append(State(state_id, name, [], color, validity_start, validity_end))
        conn.close()
        return res
    def check_reassign_state_consistency(self, to_be_reassigned_id, to_be_enlarged_id):
        conn=self.open_connection()
        with conn.cursor() as cur:
            cur.execute('''
            SELECT state_id, validity_start, validity_end
            FROM state_names 
            WHERE state_id IN %s
            ''', ((to_be_enlarged_id, to_be_reassigned_id),))
            res = cur.fetchall()
            logging.debug('RES')
            logging.debug(res)
            try : 
                to_be_enlarged = next(st for st in res if st[0]==to_be_enlarged_id)
                logging.debug(to_be_enlarged)
                to_be_reassigned = next(st for st in res if st[0]==to_be_reassigned_id)
                if to_be_enlarged[1] > to_be_reassigned[1] :
                    raise BadRequest(f'''
                        Error : the state to be reassigned starts before the target : 
                            {to_be_reassigned[1].isoformat()}<{to_be_enlarged[1].isoformat()}''')
                if to_be_enlarged[2] < to_be_reassigned[2] :
                    raise BadRequest(f'''
                                    Error : the state to be reassigned ends before the target : 
                                    {to_be_reassigned[2].isoformat()}>{to_be_enlarged[2].isoformat()}''')
            except StopIteration :
                raise NotFound(f"Could not find {to_be_reassigned_id} and {to_be_enlarged_id}") 
        conn.close()
    def reassign_state(self, to_be_reassigned_id, to_be_enlarged_id):
        assert isinstance(to_be_reassigned_id, int)
        assert isinstance(to_be_enlarged_id, int)
        self.check_reassign_state_consistency(to_be_reassigned_id, to_be_enlarged_id)
        conn = self.open_connection()
        try:
            with conn.cursor() as cur :
                cur.execute('''
                    UPDATE territories
                    SET state_id=%s
                    WHERE state_id=%s
                ''', (to_be_enlarged_id, to_be_reassigned_id))
                self.remove_empty_state(cur, to_be_reassigned_id)
                conn.commit()
                conn.close()
        except Exception as e:
            conn.rollback()
            logging.warning("canceled transaction")
            raise e
        return to_be_enlarged_id

    def check_reassign_territory_consistency(self, territory_id, state_id):
        conn=self.open_connection()
        with conn.cursor() as cur:
            cur.execute('''
                SELECT validity_start, validity_end 
                FROM territories
                WHERE territory_id=%s
            ''', (territory_id,))
            territory_period = cur.fetchone()
            if territory_period is None:
                raise NotFound(f"Cannot find territory {territory_id}")
            cur.execute('''
                SELECT validity_start, validity_end
                FROM state_names
                WHERE state_id=%s
            ''', (state_id,))
            state_period = cur.fetchone()
            if state_period is None:
                raise NotFound(f'Cannot find state {state_id}')
            if state_period[0] > territory_period[0] or state_period[1]< territory_period[1]:
                raise BadRequest(f'''
                    Cannot assign a territory with validity ({territory_period[0]}, {territory_period[1]}) 
                    that lies outside of state validity ({state_period[0]}, {state_period[1]})''')
        conn.close()

    def reassign_territory(self, territory_id, state_id):
        assert isinstance(territory_id, int)
        assert isinstance(state_id, int)
        self.check_reassign_territory_consistency(territory_id, state_id)
        conn = self.open_connection()
        try:
            with conn.cursor() as cur :
                cur.execute('''
                    SELECT state_id 
                    FROM territories
                    WHERE territory_id=%s
                ''', (territory_id,))
                old_state_id = cur.fetchone()[0]
                cur.execute('''
                    UPDATE territories
                    SET state_id=%s
                    WHERE territory_id=%s
                ''', (state_id, territory_id))
                cur.execute('''
                    SELECT COUNT(*)
                    FROM territories INNER JOIN states ON territories.state_id=states.state_id
                    WHERE territories.state_id=%s
                ''', (old_state_id,))
                row = cur.fetchone()
                logging.debug(f"COUNT retrieved for {old_state_id} : {row[0]}")
                if(row[0]==0):
                    self.remove_empty_state(cur, old_state_id)
                conn.commit()
                conn.close()
        except Exception as e:
            conn.rollback()
            logging.warning("canceled transaction")
            raise e
        return territory_id

    def remove_empty_state(self, cursor, state_id):
        cursor.execute('''
            DELETE FROM state_names 
            WHERE state_id=%s
        ''', (state_id,))
        cursor.execute('''
            DELETE FROM states 
            WHERE state_id=%s
        ''', (state_id,))

