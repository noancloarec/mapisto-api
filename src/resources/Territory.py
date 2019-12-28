from shapely.geometry import Polygon
from .helper import fill_optional_fields
from maps_geometry.compression import compress
from maps_geometry.feature_extraction import get_bounding_box
from .TerritoryShape import TerritoryShape


class Territory:
    def __init__(self, territory_id,  min_x, max_x, min_y, max_y, representations: list):
        self.territory_id = territory_id
        self.representations = representations
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    @staticmethod
    def from_dict(json_dict, precision_levels):
        json_dict = fill_optional_fields(json_dict, ['territory_id'])
        minx, miny, maxx, maxy = get_bounding_box(json_dict['d_path'])
        representations = []
        for level in precision_levels:
            representations.append(TerritoryShape(
                compress(json_dict['d_path'], level), level))
        return Territory(json_dict['territory_id'], min_x=minx, max_x=maxx, min_y=miny, max_y=maxy, representations=representations)

    def __str__(self):
        return str({
            "territory_id": self.territory_id,
            "bounding_box": str(((self.min_x, self.min_y), (self.max_x, self.max_y))),
            "representations": str([str(rep) for rep in self.representations])
        }
        )
