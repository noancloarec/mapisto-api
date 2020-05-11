from datetime import datetime
from dateutil.parser import parse
from werkzeug.exceptions import BadRequest

class StateRepresentation:
    def __init__(self, name, validity_start, validity_end, color):
        assert isinstance(name, str) or name is None
        assert isinstance(validity_start, datetime)
        assert isinstance(validity_end, datetime)
        assert isinstance(color, str) or color is None
        self.name = name
        self.validity_start = validity_start
        self.validity_end = validity_end
        self.color = color
    def is_right_after(self, other):
        assert isinstance(other, StateRepresentation)
        return self.validity_start == other.validity_end

    @staticmethod
    def from_dict(json_dict):
        start_string = json_dict['validity_start']
        end_string = json_dict['validity_end']
        try:
            validity_start = parse(start_string).replace(tzinfo=None)
            validity_end=parse(end_string).replace(tzinfo=None)
            return StateRepresentation(json_dict.get('name').strip(), validity_start, validity_end, json_dict.get('color'))
        except TypeError:
            raise BadRequest(f'Wrong date format for period : ( {start_string} , {end_string} )')
    
    def equals(self, other):
        assert isinstance(other, StateRepresentation)
        return self.validity_end==other.validity_end and self.validity_start==other.validity_start and other.color==self.color and other.name==self.name