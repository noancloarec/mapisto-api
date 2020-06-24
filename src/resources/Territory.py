from .helper import fill_optional_fields
from maps_geometry.feature_extraction import get_bounding_box
from .BoundingBox import BoundingBox
from datetime import datetime
from .MapistoShape import MapistoShape
from dateutil.parser import parse

from werkzeug.exceptions import BadRequest
class Territory:
    def __init__(self, territory_id, representations: list, state_id,  bounding_box = None,  validity_start=None, validity_end=None, color=None, name=None):
        assert isinstance(validity_start, datetime)
        assert isinstance(validity_end, datetime)
        assert isinstance(representations, list)
        assert bounding_box is None or isinstance(bounding_box, BoundingBox)
        assert color is None or isinstance(color, str)
        assert name is None or isinstance(name, str)
        assert isinstance(state_id, int)
        for representation in representations:
            assert isinstance(representation, MapistoShape)
        
        self.territory_id = territory_id
        self.representations = representations
        self.bounding_box = bounding_box
        self.validity_end = validity_end.replace(tzinfo=None)
        self.validity_start = validity_start.replace(tzinfo=None)
        self.state_id=state_id
        self.name=name
        self.color=color


    @staticmethod
    def from_dict(json_dict):
        assert isinstance(json_dict, dict), "The territory provided is not a dict"
        try :
            return Territory(json_dict.get('territory_id'),
                bounding_box=get_bounding_box(json_dict['d_path']),
                state_id=json_dict['state_id'],
                representations=[MapistoShape(json_dict['d_path'], 0)], 
                validity_start=parse(json_dict['validity_start']),
                validity_end=parse(json_dict['validity_end']),
                color=json_dict.get('color'),
                name=json_dict.get('name')
                )
        except KeyError as e:
            raise BadRequest('Json is incomplete' + str(e))
    def to_dict(self) : 
        return {
            'territory_id' : self.territory_id,
            'd_path': self.representations[0].d_path ,
            'state_id': self.state_id ,
            'validity_start' : self.validity_start ,
            'validity_end' : self.validity_end ,
            'color' : self.color ,
            'bounding_box' : self.bounding_box ,
            'name' : self.name
        }

    def __str__(self):
        return f'''
            territory_id: {self.territory_id},
            state_id : {self.state_id},
            name : {self.name},
            validity_start : {self.validity_start},
            validity_end : {self.validity_end},
            bounding_box: {self.bounding_box},
            representations: {list(map(str, self.representations))},
            color : {self.color},
        '''

    def is_outdated(self, at):
        assert isinstance(at, datetime)
        return at < self.validity_start or at >= self.validity_end
    
    def equals(self, other):
        assert isinstance(other, Territory)
        if (self.name != other.name or
            self.color != other.color or
            self.validity_start != other.validity_start or
            self.validity_end != other.validity_end or 
            not self.bounding_box.equals(other.bounding_box) or
            self.state_id != other.state_id) :
            return False
        for i in range(len(self.representations)):
            if not self.representations[i].equals(other.representations[i]):
                return False
        return True
