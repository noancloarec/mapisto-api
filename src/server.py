from flask import Flask, send_from_directory, jsonify, request, redirect
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime
from werkzeug.exceptions import BadRequest
from flask_cors import CORS
import os

from datasource.postgresql_source import PostgreSQLDataSource
from json_encoder import MapistoObjectsEncoder
from resources.State import State
from resources.Land import Land
from dateutil.parser import parse
import logging

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
    validity_start, validity_end = date_from_request('validity_start', 'validity_end')
    state = State.from_dict(request.json, precision_levels=PRECISION_LEVELS)
    return str(datasource.add_state(state, validity_start, validity_end))


@app.route('/state', methods=['PUT'])
def put_state():
    validity_start, validity_end = date_from_request('validity_start', 'validity_end')
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


@app.route('/state_from_territory/<territory_id>', methods=["GET"])
def get_state_from_territory(territory_id):
    date = date_from_request('date')
    return jsonify(datasource.get_state_from_territory(int(territory_id), date))

@app.route('/state/<state_id>', methods=["GET"])
def get_state_by_id(state_id):
    date = date_from_request('date')
    return jsonify(datasource.get_state(int(state_id), date, min(PRECISION_LEVELS))) # min precision to catch even the smallest territories


@app.route('/', methods=['GET'])
def redirectDoc():
    return redirect(API_DOC_URL)


def date_from_request(*identifiers):
    res = []
    try:
        for id in identifiers:
            res.append(parse(request.args.get(id)))
    except TypeError:
        if request.args.get(id)==None:
            raise BadRequest("Missing parameter : "+id)
        else :
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
