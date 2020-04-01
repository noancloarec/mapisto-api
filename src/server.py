import logging
import os
from datetime import datetime
from pprint import pprint

from dateutil.parser import parse
from flask import Flask, jsonify, redirect, request, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.exceptions import BadRequest, InternalServerError, HTTPException

from datasource.postgresql_source import PostgreSQLDataSource
from json_encoder import MapistoObjectsEncoder
from resources.Land import Land
import pytz
from resources.State import State

PRECISION_LEVELS = [float(prec)
                    for prec in os.environ['PRECISION_LEVELS'].split(' ')]

logging.basicConfig(level=logging.DEBUG)


datasource = PostgreSQLDataSource()

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


@app.route('/map', methods=['GET'])
def get_states():
    date = date_from_request('date')
    precision, bbmin_x, bbmax_x, bbmin_y, bbmax_y = extract_map_request()
    res = jsonify(datasource.get_states(
        date,
        precision=precision,
        bbmin_x=bbmin_x,
        bbmax_x=bbmax_x,
        bbmin_y=bbmin_y,
        bbmax_y=bbmax_y
    ))
    return res


@app.route('/state', methods=['POST'])
def post_state():
    validity_start, validity_end = date_from_request(
        'validity_start', 'validity_end')
    state = State.from_dict(request.json, precision_levels=PRECISION_LEVELS)
    return str(datasource.add_state(state, validity_start, validity_end))


@app.route('/state', methods=['PUT'])
def put_state():
    validity_start, validity_end = date_from_request(
        'validity_start', 'validity_end')
    state = State.from_dict(request.json, precision_levels=PRECISION_LEVELS)
    return str(datasource.edit_state(state, validity_start, validity_end))


@app.route('/land', methods=['POST'])
def post_land():
    land = Land.from_dict(request.json, PRECISION_LEVELS)
    return jsonify(datasource.add_land(land))


@app.route('/land', methods=['GET'])
def get_land():
    precision, bbmin_x, bbmax_x, bbmin_y, bbmax_y = extract_map_request()
    return jsonify(
        datasource.get_land(
            precision=precision,
            bbmin_x=bbmin_x,
            bbmax_x=bbmax_x,
            bbmin_y=bbmin_y,
            bbmax_y=bbmax_y
        )
    )


@app.route('/state/from_territory/<territory_id>', methods=["GET"])
def get_state_from_territory(territory_id):
    date = date_from_request('date')
    return jsonify(datasource.get_state_from_territory(int(territory_id), date))


@app.route('/state/<state_id>', methods=["GET"])
def get_state_by_id(state_id):
    date = date_from_request('date')
    # min precision to catch even the smallest territories
    return jsonify(datasource.get_state(int(state_id), date, min(PRECISION_LEVELS)))


@app.route('/state/<state_id>/concurrent_states', methods=["GET"])
def get_concurrent_states(state_id):
    start, end = date_from_request('newStart', 'newEnd')
    return jsonify(datasource.get_concurrent_states(state_id, start, end))

@app.route('/state/<state_id>/extend', methods=['PUT'])
def extend_state(state_id):
    start, end = date_from_request('newStart', 'newEnd')
    return jsonify(datasource.extend_state(state_id, start, end, request.json))

@app.route('/territory/<territory_id>/concurrent_territories', methods=["GET"])
def get_concurrent_territories(territory_id):
    start, end = date_from_request('newStart', 'newEnd')
    x, y = (float(request.args.get('capital_x')) , float(request.args.get('capital_y')))
    return jsonify(datasource.get_concurrent_territories(territory_id, start, end, x, y, min(PRECISION_LEVELS)))

@app.route('/territory/<territory_id>/extend', methods=['PUT'])
def extend_territory(territory_id) :
    start, end = date_from_request('newStart', 'newEnd')
    datasource.extend_territory(territory_id, start, end, request.json)
    return jsonify(datasource.get_territory(territory_id))


@app.route('/', methods=['GET'])
def redirectDoc():
    return redirect(API_DOC_URL)


def date_from_request(*identifiers):
    res = []
    try:
        for id in identifiers:
            res.append(parse(request.args.get(id)).replace(tzinfo=pytz.UTC))
    except TypeError:
        if request.args.get(id) == None:
            raise BadRequest("Missing parameter : "+id)
        else:
            raise BadRequest('Wrong format for '+id+' : '+request.args.get(id))
    if len(res) == 1:
        return res[0]
    else:
        return res


def extract_map_request():
    precision = float(request.args.get('precision_in_km')),
    bbmin_x = int(float(request.args.get('min_x'))),
    bbmax_x = int(float(request.args.get('max_x'))),
    bbmin_y = int(float(request.args.get('min_y'))),
    bbmax_y = int(float(request.args.get('max_y')))
    return (precision, bbmin_x, bbmax_x, bbmin_y, bbmax_y)


@app.errorhandler(HTTPException)
def handle_http(e: HTTPException):
    return e.description, e.code


@app.errorhandler(Exception)
def handle_500(e):
    logging.info("SERVER ERROR caught : ")
    logging.exception(e)
    return "Internal Server Error", 500
