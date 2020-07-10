from resources.BoundingBox import BoundingBox
from datetime import datetime
from crud.db import get_cursor
from crud.Territory_CRUD import TerritoryCRUD
from crud.Land_CRUD import LandCRUD
import functools
from math import log, floor
import logging
from crud.State_CRUD import StateCRUD
import conf
from werkzeug.exceptions import NotFound
from display_utils.precision import precision_from_bbox_and_px_width
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
                'bounding_box' : bbox,
                'date' : date
            }
    @staticmethod
    def get_evolution_by_state(state_id, pixel_width):
        assert isinstance(state_id, int)
        assert isinstance(pixel_width, float)
        with get_cursor() as cursor:
            res = []
            for date in _determine_dates_to_show(cursor, state_id):
                try :
                    bbox = StateCRUD.get_bbox(cursor, state_id, date).enlarge_to_aspect_ratio(16/9)
                    logging.error('setting last bbox')
                    last_bbox = bbox
                except NotFound:
                    bbox = last_bbox 
                precision = precision_from_bbox_and_px_width(bbox, pixel_width)
                territories = TerritoryCRUD.get_within_bbox_at_time(cursor, bbox, date, precision)
                state_ids = frozenset(t.state_id for t in territories)
                states = StateCRUD.get_many(cursor, state_ids)
                res.append({
                    'states' : states,
                    'territories' : territories,
                    'bounding_box' : bbox,
                    'date' : date,
                    'lands': LandCRUD.get_lands(cursor, bbox, precision)
                })
            return res
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
                'bounding_box' : bbox,
                'date' : date,
                'lands': LandCRUD.get_lands(cursor, bbox, precision)
            }


def _determine_dates_to_show(cursor, state_id):
    its_territories = TerritoryCRUD.get_by_state(cursor, state_id)
    if len(its_territories)==0:
        raise NotFound(f'No territories found for state {state_id}')
    start = min([t.validity_start for t in its_territories])
    end = max([t.validity_end for t in its_territories])
    end = end.replace(year=end.year-1)
    # logging.error('start : ')
    # logging.error(start.isoformat())
    if end <= start :
        return [start]
    nb_years = end.year - start.year
    nb_maps = floor(nb_years**(1/3))
    gap_per_maps = floor(nb_years / nb_maps)
    return [start.replace(year=start.year+i*gap_per_maps) for i in range(nb_maps+1)]
