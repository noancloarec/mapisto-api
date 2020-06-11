from flask.json import JSONEncoder
from resources.State import State
from resources.Land import Land
import logging
from resources.Territory import Territory
from resources.BoundingBox import BoundingBox
from werkzeug.exceptions import InternalServerError
import numpy as np
from resources.Scene import Scene
from datetime import datetime

class MapistoObjectsEncoder(JSONEncoder):
    def default(self, obj):  # pylint: disable=E0202
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(MapistoObjectsEncoder, self).default(obj)
