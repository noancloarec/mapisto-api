from flask.json import JSONEncoder
from resources.State import State
from resources.Land import Land
import logging
from resources.Territory import Territory
from werkzeug.exceptions import InternalServerError
class MapistoObjectsEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, State):
            return {
                'state_id' : obj.state_id,
                'color' : obj.color,
                'territories' : obj.territories,
                'name' : obj.name
            }
        if isinstance(obj, Territory):
            if len(obj.representations) != 1:
                raise InternalServerError("A territory should not have more or less than 1 representation for jsonify")
            return {
                'territory_id' : obj.territory_id,
                'd_path' : obj.representations[0].d_path

            }
        if isinstance(obj, Land):
            if len(obj.representations) != 1:
                raise InternalServerError("A territory should not have more or less than 1 representation for jsonify")
            return {
                'land_id' : obj.land_id,
                'd_path' : obj.representations[0].d_path

            }
        return super(MapistoObjectsEncoder, self).default(obj)