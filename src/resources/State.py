from .BoundingBox import BoundingBox
from datetime import datetime
from dateutil.parser import parse
from werkzeug.exceptions import BadRequest
from .StateRepresentation import StateRepresentation
class State:
    def __init__(self, state_id, validity_start, validity_end, representations):
        assert isinstance(validity_start, datetime)
        assert isinstance(validity_end, datetime)
        assert isinstance(representations, list)
        self.state_id = state_id
        self.validity_end = validity_end
        self.validity_start = validity_start
        self.representations = representations

    def __str__(self):
        return f"[{str(self.validity_start)}, {str(self.validity_end)}[ : (no{self.state_id})"
    
    @staticmethod
    def from_dict(json_dict):
        start_string = json_dict['validity_start']
        end_string = json_dict['validity_end']
        try:
            validity_start = parse(start_string).replace(tzinfo=None)
            validity_end=parse(end_string).replace(tzinfo=None)
        except TypeError:
            raise BadRequest(f'Wrong date format for period : ( {start_string} , {end_string} )')
        representations_json = json_dict['representations']
        if not isinstance(representations_json, list) or len(representations_json)==0:
            raise BadRequest("The state must have at least one representation that covers the state lifespan")
        representations = []
        for i, rep_json in enumerate(representations_json) :
            rep = StateRepresentation.from_dict(rep_json)
            if i>0 and not rep.is_right_after(representations[i-1]):
                raise BadRequest(f"The state representation {rep_json} must be right after {representations_json[i-1]}")
            representations.append(rep)
        representations_start = representations[0].validity_start
        representations_end = representations[len(representations)-1].validity_end
        if representations_start != validity_start or representations_end != validity_end:
            raise BadRequest(f"The representations of the state go from {representations_start} to {representations_end} : it should go from {validity_start} to {validity_end} (i.e. the state's validity)")
        return State(json_dict.get('state_id'), validity_start= validity_start, validity_end=validity_end, representations=representations)
    
    # does not compare ids
    def equals(self, other):
        assert isinstance(other, State)
        if other.validity_start != self.validity_start or other.validity_end != self.validity_end or len(self.representations) != len(other.representations):
            return False
        for i, rep in enumerate(self.representations):
            other_rep = other.representations[i]
            assert isinstance(rep, StateRepresentation)
            assert isinstance(other_rep, StateRepresentation)
            if not rep.equals(other_rep):
                return False
        return True
