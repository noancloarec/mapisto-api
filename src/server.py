import logging
import os
from datetime import datetime
from pprint import pprint
from resources.BoundingBox import BoundingBox
from dateutil.parser import parse, ParserError
from flask import Flask,  redirect, request, send_from_directory
from flask_cors import CORS, cross_origin
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.exceptions import BadRequest, InternalServerError, HTTPException
from exceptions.mapisto_exceptions import MapistoException
from json_encoder import MapistoObjectsEncoder
from resources.Land import Land
import pytz
from resources.State import State
from land_tag import LandTag
from territory_tag import TerritoryTag
from map_tag import MapTag
from resources.Territory import Territory
from state_tag import StateTag
from movie_tag import MovieTag
from flask_compress import Compress
# from elasticapm.contrib.flask import ElasticAPM
import time

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)
Compress(app)

"""
# Does not send transactions (only errors) if flask_debug is on
if not app.debug:
    logging.info('Initializing APM agent')
    app.config['ELASTIC_APM'] = {
    # Set required service name. Allowed characters:
    # a-z, A-Z, 0-9, -, _, and space
    'SERVICE_NAME': os.environ.get('SERVICE_NAME'),

    # Use if APM Server requires a token
    'SECRET_TOKEN': '',

        'SERVER_URL': 'http://apm-server:8200'
    }
    apm = ElasticAPM(app)
"""

# app.config['CORS_HEADERS'] = 'Content-Type'
app.json_encoder = MapistoObjectsEncoder

SWAGGER_URL = '/docs'  # URL for exposing Swagger UI (without trailing '/')
OPENAPI_PATH = '/static/openapi.yaml'
API_DOC_URL = '/docs'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    OPENAPI_PATH,
    config={  # Swagger UI config overrides
        'app_name': "Mapisto"
    },
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)



@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/test', methods=['GET'])
def test():
    time.sleep(1)
    if time.time_ns() %2 == 0:
        return 'test success'
    else:
        return 'bad request', 400

@app.route('/map', methods=['GET'])
def get_map():
    date = date_from_request('date')
    precision, bbox = extract_map_request()
    return MapTag.get(bbox, date, precision)

@app.route('/map_for_state/<int:state_id>', methods=['GET'])
def get_map_by_state(state_id):
    date = date_from_request('date')
    logging.debug(request.args)
    pixel_width = float(request.args.get('pixel_width'))
    return MapTag.get_by_state(state_id, date, pixel_width)

@app.route('/gif_map_for_state/<int:state_id>', methods=['GET'])
def get_maps_by_state(state_id):
    pixel_width = float(request.args.get('pixel_width'))
    return {
        "maps" : MapTag.get_evolution_by_state(state_id, pixel_width)
        }

@app.route('/map_for_territory/<int:territory_id>', methods=['GET'])
def get_map_by_territory(territory_id):
    date = date_from_request('date')
    pixel_width = float(request.args.get('pixel_width'))
    return MapTag.get_by_territory(territory_id, date, pixel_width)

@app.route('/state', methods=['POST'])
def post_state():
    return { "added_state" : StateTag.post(State.from_dict(request.json)) }

@app.route('/state', methods=['PUT'])
def put_state():
    absorb = request.args.get('absorb_conflicts')
    return { "modified_state" : StateTag.put(State.from_dict(request.json),  absorb=='True' or absorb=='true')}

@app.route('/merge_state/<int:state_id>/into/<int:sovereign_state_id>', methods=['PUT'])
def merge_states(state_id, sovereign_state_id):
    return {
        "merged_into" : StateTag.merge(state_id, sovereign_state_id)
    }


@app.route('/state/<int:state_id>', methods=['GET'])
def get_state(state_id):
    return StateTag.get(state_id).to_dict()

@app.route('/state/<int:state_id>/movie', methods=['GET'])
def get_state_movie(state_id):
    pixel_width = float(request.args.get('pixel_width'))
    return {"scenes" : MovieTag.get_by_state(state_id, pixel_width)}

@app.route('/state_search', methods=['GET'])
def search_state():
    pattern = request.args.get('pattern')
    if not pattern or not pattern.strip():
        raise BadRequest('Empty pattern to search')
    return {"search_results" : StateTag.search(pattern.strip()) }

@app.route('/territory', methods=['POST'])
def post_territory():
    return {"added_territory" : TerritoryTag.post(Territory.from_dict(request.json)) }

@app.route('/territory', methods=['PUT'])
def put_territory():
    return { "modified_territory" : TerritoryTag.put(Territory.from_dict(request.json)) }

@app.route('/territory/<int:territory_id>', methods=['GET'])
def get_territory(territory_id):
    return TerritoryTag.get(territory_id).to_dict()

@app.route('/territory/<int:territory_id>', methods=['DELETE'])
def delete_territory(territory_id):
    return {"deleted_territory" : TerritoryTag.delete(territory_id)}


@app.route('/land', methods=['POST'])
def post_land():
    land = Land.from_dict(request.json)
    return {"added_land" : LandTag.post_land(land)}


@app.route('/land', methods=['GET'])
def get_land():
    precision, bbox = extract_map_request()
    return {"lands" : LandTag.get_lands(bbox, precision)}

@app.route('/', methods=['GET'])
def redirectDoc():
    return redirect(API_DOC_URL)


def date_from_request(*identifiers):
    res = []
    try:
        for id in identifiers:
            res.append(parse(request.args.get(id)).replace(tzinfo=None))
    except (TypeError, ParserError):
        if request.args.get(id) == None:
            raise BadRequest("Missing parameter : "+id)
        else:
            raise BadRequest('Wrong format for '+id+' : '+request.args.get(id))
    if len(res) == 1:
        return res[0]
    else:
        return res


def extract_map_request():
    precision = float(request.args.get('precision_in_km'))
    bbmin_x = int(float(request.args.get('min_x')))
    bbmax_x = int(float(request.args.get('max_x')))
    bbmin_y = int(float(request.args.get('min_y')))
    bbmax_y = int(float(request.args.get('max_y')))
    bbox = BoundingBox(bbmin_x, bbmin_y, bbmax_x-bbmin_x, bbmax_y-bbmin_y)
    return (precision, bbox)

@app.errorhandler(MapistoException)
def handle_merge_state_conflict(e):
    logging.debug(vars(e))
    return {
        "description" : e.description,
        "data" : e.response
    }, e.code


@app.errorhandler(HTTPException)
def handle_http(e: HTTPException):
    return e.description, e.code


@app.errorhandler(Exception)
def handle_500(e):
    logging.info("SERVER ERROR caught : ")
    # if not app.debug:
    #     apm.capture_exception()
    logging.exception(e)
    return "Internal Server Error", 500
