from crud.State_CRUD import StateCRUD
from crud.Territory_CRUD import TerritoryCRUD
import numpy as np
import logging
from datetime import datetime
import copy
from crud.db import get_cursor
import functools
from crud.Land_CRUD import LandCRUD
from display_utils.precision import precision_from_bbox_and_px_width

class MovieTag:
    @staticmethod
    def get_by_state(state_id, pixel_width):
        assert isinstance(state_id, int)        
        with get_cursor() as cursor:
            viewboxes = _get_all_viewboxes_by_period(cursor, state_id)
            viewboxes_harmony = _merge_similar_viewboxes(viewboxes)
            for vb in viewboxes_harmony:
                vb['bbox'] = vb['bbox'].enlarge_to_aspect_ratio(16/9).resize(1.2)
            res = []
            for vb in viewboxes_harmony:
                precision =  precision_from_bbox_and_px_width(vb['bbox'], pixel_width)
                territories = TerritoryCRUD.get_within_bbox_in_period(cursor, vb['bbox'], vb['start'], vb['end'],precision)
                states = StateCRUD.get_many(cursor, [t.state_id for t in territories])
                res.append({
                    'territories' : territories,
                    'states' : states,
                    'validity_start' : vb['start'],
                    'validity_end' : vb['end'],
                    'bounding_box' : vb['bbox'],
                    'lands' : LandCRUD.get_lands(cursor, vb['bbox'], precision)
                })
            return res
            # # Some period may be empty for a state, the viewbox shall be the same as the previous one
            # for i, bbox in enumerate(bbox_by_period):
            #     if bbox is None:
            #         bbox_by_period[i] = bbox_by_period[i-1]
            # return [Scene(changeDates[i], changeDates[i+1], bbox) for i, bbox in enumerate(bbox_by_period)]


def _get_all_viewboxes_by_period(cursor, state_id):
    territories = TerritoryCRUD.get_by_state(cursor, state_id)
    change_dates = np.sort(np.unique([t.validity_start for t in territories] + [t.validity_end for t in territories]))
    bbox_list_by_period = [{
            'start' : change_date,
            'end' : change_dates[i+1] if i+1 < len(change_dates) else max(change_dates) ,
            'bboxes' : [t.bounding_box for t in territories if not t.is_outdated(change_date)]
        } for i,change_date in enumerate(change_dates)]
    bbox_list_by_period = [bb_list for bb_list in bbox_list_by_period if len(bb_list['bboxes'])]
    for i, bb_list in enumerate(bbox_list_by_period[:-1]):
        bb_list['end'] = bbox_list_by_period[i+1]['start']
    bbox_by_period = [{
        'start' : bbox_list['start'],
        'end' : bbox_list['end'],
        'bbox' : _merge_bboxes(bbox_list['bboxes'])
    } for bbox_list in bbox_list_by_period]
    return bbox_by_period

def _merge_similar_viewboxes(bbox_by_period):
    bbox_by_period = copy.deepcopy(bbox_by_period)
    for i in range(len(bbox_by_period)-1):
        current = bbox_by_period[i]
        next_bbox = bbox_by_period[i+1]
        if current['bbox'].get_area_percentage_in_common(next_bbox['bbox']) > 10:
            union = {
                'start' : current['start'],
                'end' : next_bbox['end'],
                'bbox' : current['bbox'].union(next_bbox['bbox'])
            }
            bbox_by_period[i] = union
            bbox_by_period[i+1] = union
    for vb in bbox_by_period :
        logging.debug({"start" : vb['start'], 'end' : vb['end']})

    res = []
    for i in range(len(bbox_by_period)-1):
        if bbox_by_period[i]['start'] != bbox_by_period[i+1]['start']:
            res.append(bbox_by_period[i])
    res.append(bbox_by_period[-1])
    return res
    
def _merge_bboxes(bboxes):
    return functools.reduce(lambda a,b : a.union(b), bboxes)