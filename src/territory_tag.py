from resources.Territory import Territory
from resources.State import State
from crud.State_CRUD import StateCRUD
from crud.Territory_CRUD import TerritoryCRUD
from crud.db import get_cursor
from werkzeug.exceptions import Conflict
from maps_geometry.consistency import territories_conflict
from maps_geometry.compression import compress_territory
from werkzeug.exceptions import BadRequest
from color_utils.color_utils import colour_distance
import logging

class TerritoryTag:
    @staticmethod
    def post(territory):
        assert isinstance(territory, Territory)
        with get_cursor() as cursor:
            state = StateCRUD.get(cursor, territory.state_id)
            if territory.validity_start < state.validity_start or territory.validity_end > state.validity_end:
                raise Conflict(f"Cannot add territory ({territory.validity_start} , {territory.validity_end}) to state ({state.validity_start}, {state.validity_end}) : period overflows")
            potentially_intersecting = TerritoryCRUD.get_within_bbox_in_period(cursor, territory.bounding_box, territory.validity_start, territory.validity_end, 0) 
            t_conflict_ids = [other.territory_id for other in potentially_intersecting if territories_conflict(territory, other)]
            if len(t_conflict_ids):
                raise Conflict(f"Cannot add the territory : it conflicts with territories {t_conflict_ids}")
            compressed_territory = compress_territory(territory)
            return TerritoryCRUD.add(cursor, compressed_territory)
    @staticmethod
    def get(territory_id):
        with get_cursor() as cursor:
            territory = TerritoryCRUD.get(cursor, territory_id)
            assert territory.representations[0].precision_in_km == 0
            return territory

    @staticmethod
    def count():
        with get_cursor() as cursor:
            return TerritoryCRUD.count(cursor)


    @staticmethod
    def delete(territory_id):
        with get_cursor() as cursor:
            TerritoryCRUD.delete(cursor, territory_id)

    @staticmethod
    def put(territory):
        assert isinstance(territory, Territory)
        with get_cursor() as cursor:
            original_territory = TerritoryCRUD.get(cursor, territory.territory_id)
            if original_territory.state_id != territory.state_id:
                TerritoryTag._assign_to_state(cursor, original_territory, territory.state_id)
        return territory

    '''
    Returns the created territories ids
    '''
    @staticmethod
    def _assign_to_state(cursor, territory, target_state_id):
        assert isinstance(territory, Territory)
        assert isinstance(target_state_id, int)
        created_territories_ids = []
        target_state = StateCRUD.get(cursor, target_state_id)
        if target_state.validity_end <= territory.validity_start or target_state.validity_start >= territory.validity_end :
            raise BadRequest(f'The territory goes from {territory.validity_start} to {territory.validity_end} and has no time in common with state from {target_state.validity_start} to {target_state.validity_end}')
        if target_state.validity_end < territory.validity_end :
            to_add_at_end = Territory(None, territory.representations, territory.state_id, territory.bounding_box, target_state.validity_end, territory.validity_end, territory.color, territory.name)
            created_territories_ids.append(TerritoryCRUD.add(cursor, to_add_at_end))
            territory.validity_end = target_state.validity_end
            TerritoryCRUD.edit(cursor, territory, change_end=True)
        if target_state.validity_start > territory.validity_start:
            to_add_at_start = Territory(None, territory.representations, territory.state_id, territory.bounding_box, territory.validity_start, target_state.validity_start, territory.color, territory.name)
            created_territories_ids.append(TerritoryCRUD.add(cursor, to_add_at_start))
            territory.validity_start = target_state.validity_start
            TerritoryCRUD.edit(cursor, territory, change_start=True)
        new_color = TerritoryTag._get_color_for_territory(territory, StateCRUD.get(cursor, territory.state_id), target_state)
        if new_color != territory.color:
            territory.color = new_color
            TerritoryCRUD.edit(cursor, territory, change_color=True)
        territory.state_id = target_state.state_id
        TerritoryCRUD.edit(cursor, territory, change_state_id=True)
        return created_territories_ids

    @staticmethod
    def _get_color_for_territory(territory, old_state, new_state):
        assert isinstance(territory, Territory)
        assert isinstance(old_state, State)
        assert isinstance(new_state, State)
        old_color = territory.color if territory.color else _get_contemporaneous_color(territory, old_state)
        new_color = _get_contemporaneous_color(territory, new_state)
        if not old_color or not new_color:
            return new_color
        logging.error(f"Colour distance : between {old_color} and {new_color}")
        logging.error(colour_distance(old_color, new_color))
        if colour_distance(old_color, new_color) < 15:
            # No need for a specific territory color if it is similar to new state color
            return None
        else:
            # If colour chanes between old and new, territory must record the old color itself
            return old_color

def _get_contemporaneous_color (territory, state):
    return next(r.color for r in state.representations if territory.validity_start >= r.validity_start)
