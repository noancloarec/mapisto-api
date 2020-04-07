from datetime import datetime
from .BoundingBox import BoundingBox
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
        in_km = lambda pt : 40000/2200 * pt
        if in_km(self.bbox.width) < 500:
            return 1
        elif in_km(self.bbox.width) < 2000:
            return 5
        elif in_km(self.bbox.width) < 4000:
            return 10
        elif in_km(self.bbox.width) < 8000:
            return 20
        else:
            return 50