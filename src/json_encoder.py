from flask.json import JSONEncoder
from resources.State import State

class MapistoObjectsEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, State):
            return {
                'state_id' : obj.state_id,
                'color' : obj.color,
                'territories' : obj.territories,
                'name' : obj.name
            }
        return super(MapistoObjectsEncoder, self).default(obj)