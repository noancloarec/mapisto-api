from flask.json import JSONEncoder
from resources.State import State
from resources.Land import Land
import logging
from resources.Territory import Territory
from resources.BoundingBox import BoundingBox
from werkzeug.exceptions import InternalServerError


class MapistoObjectsEncoder(JSONEncoder):
    def mapState(self, obj:State):
        res = {
            'state_id': obj.state_id,
            'name': obj.name
        }
        if hasattr(obj, 'territories') and obj.territories is not None :
            res['territories'] = obj.territories
        if hasattr(obj, 'color') and obj.color is not None:
            res['color'] = obj.color
        if hasattr(obj, 'validity_start') and obj.validity_start is not None:
            res['validity_start'] = obj.validity_start.isoformat()
        if hasattr(obj, 'validity_end') and obj.validity_end is not None:
            res['validity_end'] = obj.validity_end.isoformat()
        if hasattr(obj, 'bounding_box') and obj.bounding_box is not None:
            res['bounding_box'] = obj.bounding_box
        return res

    def default(self, obj):
        if isinstance(obj, State):
            return self.mapState(obj)
        if isinstance(obj, Territory):
            if len(obj.representations) != 1:
                raise InternalServerError(
                    "A territory should not have more or less than 1 representation for jsonify")
            return {
                'territory_id': obj.territory_id,
                'd_path': obj.representations[0].d_path,
                'validity_start' : obj.validity_start,
                'validity_end' : obj.validity_end

            }
        if isinstance(obj, Land):
            if len(obj.representations) != 1:
                raise InternalServerError(
                    "A territory should not have more or less than 1 representation for jsonify")
            return {
                'land_id': obj.land_id,
                'd_path': obj.representations[0].d_path

            }
        if isinstance(obj, BoundingBox):
            return {
                "x" : obj.x ,
                "y" : obj.y ,
                "width" : obj.width ,
                "height" : obj.height 
            }
        return super(MapistoObjectsEncoder, self).default(obj)
