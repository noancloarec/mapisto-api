from .helper import fill_optional_fields
from maps_geometry.compression import compress
from maps_geometry.feature_extraction import get_bounding_box
from .TerritoryShape import TerritoryShape
from .BoundingBox import BoundingBox
from datetime import datetime
from dateutil.parser import parse

class Territory:
    def __init__(self, territory_id, representations: list,  bounding_box = None,  validity_start=None, validity_end=None, state_id=None):
        assert isinstance(validity_start, datetime)
        assert isinstance(validity_end, datetime)
        assert isinstance(representations, list)
        assert bounding_box is None or isinstance(bounding_box, BoundingBox)
        for representation in representations:
            assert isinstance(representation, TerritoryShape)
        self.territory_id = territory_id
        self.representations = representations
        self.bounding_box = bounding_box
        self.validity_end = validity_end
        self.validity_start = validity_start
        self.state_id=state_id


    @staticmethod
    def from_dict(json_dict, precision_levels):
        assert isinstance(json_dict, dict), "The territory provided is not a dict"
        json_dict = fill_optional_fields(json_dict, ['territory_id'])
        minx, miny, maxx, maxy = get_bounding_box(json_dict['d_path'])
        representations = []
        for level in precision_levels:
            shape = compress(json_dict['d_path'], level)
            if shape :
                representations.append(TerritoryShape(shape, level))
        return Territory(json_dict['territory_id'],
            bounding_box=BoundingBox(minx, miny , maxx-minx, maxy-miny),
             representations=representations, 
             validity_start=parse(json_dict['validity_start']),
             validity_end=parse(json_dict['validity_end'])
             )

    def __str__(self):
        return str({
            "territory_id": self.territory_id,
            "bounding_box": str(self.bounding_box),
            "representations": str([str(rep) for rep in self.representations])
        }
        )

    def is_outdated(self, at:datetime):
        assert isinstance(at, datetime)
        return at < self.validity_start or at>= self.validity_end
