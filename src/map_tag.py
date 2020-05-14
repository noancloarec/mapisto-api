from resources.BoundingBox import BoundingBox
from datetime import datetime
from crud.db import get_cursor
from crud.Territory_CRUD import TerritoryCRUD
from crud.State_CRUD import StateCRUD
class MapTag:
    @staticmethod
    def get(bbox, date, precision_level):
        assert isinstance(bbox, BoundingBox)
        assert isinstance(date, datetime)
        assert date.tzinfo is None
        with get_cursor() as cursor:
            territories = TerritoryCRUD.get_within_bbox_at_time(cursor, bbox, date, precision_level)
            state_ids = frozenset(t.state_id for t in territories)
            states = [StateCRUD.get(cursor, st_id) for st_id in state_ids]
            return {
                'states' : states,
                'territories' : territories
            }
