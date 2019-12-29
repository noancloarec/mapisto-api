from .helper import fill_optional_fields
from maps_geometry.compression import compress
from maps_geometry.feature_extraction import get_bounding_box
from .LandShape import LandShape

class Land:
    def __init__(self, land_id, representations: list,  min_x=None, max_x=None, min_y=None, max_y=None):
        self.land_id = land_id
        self.representations = representations
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    @staticmethod
    def from_dict(json_dict, precision_levels):
        json_dict = fill_optional_fields(json_dict, ['land_id'])
        minx, miny, maxx, maxy = get_bounding_box(json_dict['d_path'])
        representations = []
        for level in precision_levels:
            shape = compress(json_dict['d_path'], level)
            if shape :
                representations.append(LandShape(shape, level))
        return Land(json_dict['land_id'], min_x=minx, max_x=maxx, min_y=miny, max_y=maxy, representations=representations)

    def __str__(self):
        return str({
            "land_id": self.land_id,
            "bounding_box": str(((self.min_x, self.min_y), (self.max_x, self.max_y))),
            "representations": str([str(rep) for rep in self.representations])
        })
