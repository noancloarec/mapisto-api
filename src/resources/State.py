from .helper import fill_optional_fields
from .Territory import Territory
class State:
    def __init__(self, state_id,name, territories, color):
        self.state_id = state_id
        self.territories = territories
        self.color = color
        self.name = name
    
    @staticmethod
    def from_dict(json_dict, precision_levels):
        # Name and state id do not have to be defined
        json_dict = fill_optional_fields(json_dict, ['name', 'state_id'])
        territories = [Territory.from_dict(territory_dict, precision_levels=precision_levels) for territory_dict in json_dict['territories']]
        return State(json_dict['state_id'], json_dict['name'], territories, json_dict['color'])
    