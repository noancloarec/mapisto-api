from .helper import fill_optional_fields
from maps_geometry.feature_extraction import get_bounding_box
from .MapistoShape import MapistoShape
from .BoundingBox import BoundingBox

class Land:
    def __init__(self, land_id, representations: list,  bounding_box):
        assert isinstance(bounding_box, BoundingBox)
        assert isinstance(representations, list)
        self.land_id = land_id
        self.representations = representations
        self.bounding_box = bounding_box

    @staticmethod
    def from_dict(json_dict):
        json_dict = fill_optional_fields(json_dict, ['land_id'])
        bounding_box = get_bounding_box(json_dict['d_path'])
        representations = [MapistoShape(json_dict['d_path'], 0)]
        return Land(json_dict['land_id'], bounding_box=bounding_box, representations=representations)

    def __str__(self):
        return str({
            "land_id": self.land_id,
            "representations": str([str(rep) for rep in self.representations])
        })
    
    def equals(self, other):
        if not isinstance(other, Land):
            return False
        if other.land_id!=self.land_id:
            return False
        if len(self.representations) != len(other.representations):
            return False
        if not self.bounding_box.equals(other.bounding_box):
            return False
        for i in range(len(self.representations)):
            if not self.representations[i].equals(other.representations[i]):
                return False
        
        return True