from resources.Territory import Territory
from crud.State_CRUD import StateCRUD
from crud.Territory_CRUD import TerritoryCRUD
from crud.db import get_cursor
from werkzeug.exceptions import Conflict
from maps_geometry.consistency import territories_conflict
from maps_geometry.compression import compress_territory
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
            territory.representations = [territory.representations[0]]
            return territory
