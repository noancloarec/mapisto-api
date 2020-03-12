from .helper import fill_optional_fields
from .Territory import Territory
class State:
    def __init__(self, state_id,name, territories=None, color=None, validity_start=None, validity_end=None):
        self.state_id = state_id
        self.territories = territories
        self.color = color
        self.name = name
        self.validity_end = validity_end
        self.validity_start = validity_start
    
    @staticmethod
    def from_dict(json_dict, precision_levels):
        # Name and state id do not have to be defined
        json_dict = fill_optional_fields(json_dict, ['name', 'state_id', 'territories', 'color'])
        if json_dict['territories']is None:
            territories = []
        else :
            territories = [Territory.from_dict(territory_dict, precision_levels=precision_levels) for territory_dict in json_dict['territories']]
        return State(json_dict['state_id'], json_dict['name'], territories, json_dict['color'])
    