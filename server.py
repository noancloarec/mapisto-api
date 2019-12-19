from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint



app = Flask(__name__)

SWAGGER_URL = '/docs' # URL for exposing Swagger UI (without trailing '/')
API_URL = 'http://localhost:5000/static/openapi.yaml' # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
SWAGGER_URL, # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
API_URL,
config={ # Swagger UI config overrides
    'app_name': "Mapisto"
    },
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/')
def hello_world():
    return 'Hello, World!'