from random import randint

class State:
    def __init__(self, state_id,name, territories, color):
        self.state_id = state_id
        self.territories = territories
        self.color = color
        self.name = name
    
    @staticmethod
    def from_dict(json_dict):
        print('received color : ', json_dict['color'])
        try:
            json_dict['color']
        #throw when no color OR color not hexable
        except KeyError:
            #random hex color
            json_dict['color'] = ('000000'+hex(randint(0, 16**6))[2:])[-6:]
        try:
            json_dict['state_id']
        except KeyError:
            json_dict['state_id'] = None
        try :
            json_dict['name']
        except KeyError :
            json_dict['name'] = None
        return State(json_dict['state_id'], json_dict['name'], json_dict['territories'], json_dict['color'])
    