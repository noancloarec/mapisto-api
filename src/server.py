import logging
import os
from datetime import datetime
from pprint import pprint
from resources.BoundingBox import BoundingBox
from dateutil.parser import parse, ParserError
from flask import Flask, jsonify, redirect, request, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.exceptions import BadRequest, InternalServerError, HTTPException

from json_encoder import MapistoObjectsEncoder
from resources.Land import Land
import pytz
from resources.State import State
from land_tag import LandTag


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'
app.json_encoder = MapistoObjectsEncoder

SWAGGER_URL = '/docs'  # URL for exposing Swagger UI (without trailing '/')
# Our API url (can of course be a local resource)
OPENAPI_PATH = '/static/openapi.yaml'
API_DOC_URL = '/docs'
# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
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


# @app.route('/map', methods=['GET'])
# def get_states():
#     date = date_from_request('date')
#     precision, bbmin_x, bbmax_x, bbmin_y, bbmax_y = extract_map_request()
#     logging.debug("GET")
#     res = jsonify(datasource.get_states_at(
#         date, 
#         precision=precision,
#         bbmin_x=bbmin_x,
#         bbmax_x=bbmax_x,
#         bbmin_y=bbmin_y,
#         bbmax_y=bbmax_y
#     ))
#     return res


# @app.route('/state', methods=['POST'])
# def post_state():
#     state = State.from_dict(request.json, precision_levels=PRECISION_LEVELS)
#     return str(datasource.add_state(state))


# @app.route('/state', methods=['PUT'])
# def put_state():
#     validity_start, validity_end = date_from_request(
#         'validity_start', 'validity_end')
#     state = State.from_dict(request.json, precision_levels=PRECISION_LEVELS)
#     return str(datasource.edit_state(state, validity_start, validity_end))


@app.route('/land', methods=['POST'])
def post_land():
    land = Land.from_dict(request.json)
    return jsonify(LandTag.post_land(land))


@app.route('/land', methods=['GET'])
def get_land():
    precision, bbox = extract_map_request()
    return jsonify(LandTag.get_lands(bbox, precision))


# @app.route('/state/from_territory/<territory_id>', methods=["GET"])
# def get_state_from_territory(territory_id):
#     date = date_from_request('date')
#     return jsonify(datasource.get_state_from_territory(int(territory_id), date))


# @app.route('/state/<state_id>', methods=["GET"])
# def get_state_by_id(state_id):
#     date = date_from_request('date')
#     # min precision to catch even the smallest territories
#     return jsonify(datasource.get_state(int(state_id), date, min(PRECISION_LEVELS)))

# @app.route('/state/<state_id>/split', methods=["PUT"])
# def split_state(state_id):
#     date = date_from_request('date')
#     return jsonify(datasource.split_state(int(state_id), date))


# @app.route('/state/<state_id>/concurrent_states', methods=["GET"])
# def get_concurrent_states(state_id):
#     start, end = date_from_request('newStart', 'newEnd')
#     return jsonify(datasource.get_concurrent_states(state_id, start, end))

# @app.route('/state/<state_id>/extend', methods=['PUT'])
# def extend_state(state_id):
#     start, end = date_from_request('newStart', 'newEnd')
#     return jsonify(datasource.extend_state(state_id, start, end, request.json))

# @app.route('/territory/<territory_id>/concurrent_territories', methods=["GET"])
# def get_concurrent_territories(territory_id):
#     start, end = date_from_request('newStart', 'newEnd')
#     x, y = (float(request.args.get('capital_x')) , float(request.args.get('capital_y')))
#     return jsonify(datasource.get_concurrent_territories(territory_id, start, end, x, y, min(PRECISION_LEVELS)))

# @app.route('/territory/<territory_id>/extend', methods=['PUT'])
# def extend_territory(territory_id) :
#     start, end = date_from_request('newStart', 'newEnd')
#     datasource.extend_territory(territory_id, start, end, request.json)
#     return jsonify(datasource.get_territory(territory_id))

# @app.route('/state_search', methods=['GET'])
# def searchStates():
#     try :
#         start,end=date_from_request('start', 'end')
#     except BadRequest:
#         start, end = None, None
#     pattern = request.args.get('pattern')
#     return jsonify(datasource.search_states(pattern, start, end))

# @app.route('/state/<state_id>/absorb/<to_be_absorbed_id>', methods=['PUT'])
# def absorb_state(state_id, to_be_absorbed_id):
#     return jsonify(datasource.reassign_state(int(to_be_absorbed_id), int(state_id)))

# @app.route('/territory/<territory_id>/reassign_to/<state_id>', methods=['PUT'])
# def reassign_territory(territory_id, state_id):
#     return jsonify(datasource.reassign_territory(int(territory_id), int(state_id)))

# @app.route('/movie/<state_id>', methods=['GET'])
# def get_movie(state_id):
#     return jsonify(videoSource.get_video(int(state_id)))

@app.route('/', methods=['GET'])
def redirectDoc():
    return redirect(API_DOC_URL)


def date_from_request(*identifiers):
    res = []
    try:
        for id in identifiers:
            res.append(parse(request.args.get(id)).replace(tzinfo=pytz.UTC))
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
    logging.debug(bbmax_x)
    bbox = BoundingBox(bbmin_x, bbmin_y, bbmax_x-bbmin_x, bbmax_y-bbmin_y)
    return (precision, bbox)


@app.errorhandler(HTTPException)
def handle_http(e: HTTPException):
    return e.description, e.code


@app.errorhandler(Exception)
def handle_500(e):
    logging.info("SERVER ERROR caught : ")
    logging.exception(e)
    return "Internal Server Error", 500
