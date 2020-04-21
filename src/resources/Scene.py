from datetime import datetime
from .BoundingBox import BoundingBox
import os
import functools
import logging
class Scene:
    def __init__(self, validity_start, validity_end, bbox, states=[], lands=[]):
        assert isinstance(validity_start, datetime )
        assert isinstance(validity_end, datetime)
        assert isinstance(bbox, BoundingBox)
        assert isinstance(states, list)
        assert isinstance(lands, list)
        self.validity_start = validity_start
        self.validity_end = validity_end
        self.bbox = bbox
        self.states = states
        self.lands = lands

    def get_precision(self):
        km_per_pt= 1100/40000 * self.bbox.width
        required_precision = .5*km_per_pt
        logging.debug(f'Kilometers per point : {km_per_pt}')
        precision_levels = [int(level) for level in os.environ['PRECISION_LEVELS'].split(' ')]
        return functools.reduce(lambda prev,curr : curr if abs(curr - required_precision) < abs(prev - required_precision) else prev , precision_levels )