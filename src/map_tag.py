from resources.BoundingBox import BoundingBox
from datetime import datetime
from crud.db import get_cursor
from crud.Territory_CRUD import TerritoryCRUD
import functools
from crud.State_CRUD import StateCRUD
import conf
class MapTag:
    @staticmethod
    def get(bbox, date, precision_level):
        assert isinstance(bbox, BoundingBox)
        assert isinstance(date, datetime)
        assert date.tzinfo is None
        with get_cursor() as cursor:
            territories = TerritoryCRUD.get_within_bbox_at_time(cursor, bbox, date, precision_level)
            state_ids = frozenset(t.state_id for t in territories)
            states = StateCRUD.get_many(cursor, state_ids)
            return {
                'states' : states,
                'territories' : territories
            }
    
    @staticmethod
    def get_by_state(state_id, date, pixel_width):
        assert isinstance(state_id, int)
        assert isinstance(date, datetime)
        assert isinstance(pixel_width, float)
        with get_cursor() as cursor:
            bbox = StateCRUD.get_bbox(cursor, state_id, date).enlarge_to_aspect_ratio(16/9)
            precision = precision_from_bbox_and_px_width(bbox, pixel_width)
            territories = TerritoryCRUD.get_within_bbox_at_time(cursor, bbox, date, precision)
            state_ids = frozenset(t.state_id for t in territories)
            states = StateCRUD.get_many(cursor, state_ids)
            return {
                'states' : states,
                'territories' : territories,
                'bounding_box' : bbox
            }

    @staticmethod
    def get_by_territory(territory_id, date, pixel_width):
        assert isinstance(territory_id, int)
        assert isinstance(date, datetime)
        assert isinstance(pixel_width, float)
        with get_cursor() as cursor:
            territory = TerritoryCRUD.get(cursor, territory_id)
            bbox = territory.bounding_box.enlarge_to_aspect_ratio(16/9)
            precision = precision_from_bbox_and_px_width(bbox, pixel_width)
            territories = TerritoryCRUD.get_within_bbox_at_time(cursor, bbox, date, precision)
            state_ids = frozenset(t.state_id for t in territories)
            states = StateCRUD.get_many(cursor, state_ids)
            return {
                'states' : states,
                'territories' : territories,
                'bounding_box' : bbox
            }

def precision_from_bbox_and_px_width(bbox, pixel_width):
    assert isinstance(bbox, BoundingBox)
    km_per_pt= 1100/40000 * bbox.width
    required_precision = .5*km_per_pt
    return functools.reduce(lambda prev,curr : curr if abs(curr - required_precision) < abs(prev - required_precision) else prev , conf.PRECISION_LEVELS )


