import os

PRECISION_LEVELS = [float(prec)
                    for prec in os.environ['PRECISION_LEVELS'].split(' ')]

MAPISTO_DB_HOST = os.environ.get('MAPISTO_DB_HOST')
MAPISTO_DB_NAME = os.environ.get('MAPISTO_DB_NAME')
MAPISTO_DB_USER = os.environ.get('MAPISTO_DB_USER')
MAPISTO_DB_PORT = os.environ.get('MAPISTO_DB_PORT')
MAPISTO_DB_PASSWORD = os.environ.get('MAPISTO_DB_PASSWORD')

PRODUCTION = os.environ.get('PRODUCTION')== 'TRUE'

MAPISTO_DB_HOST_TEST = os.environ.get('MAPISTO_DB_HOST_TEST')
MAPISTO_DB_NAME_TEST = os.environ.get('MAPISTO_DB_NAME_TEST')
MAPISTO_DB_USER_TEST = os.environ.get('MAPISTO_DB_USER_TEST')
MAPISTO_DB_PORT_TEST = os.environ.get('MAPISTO_DB_PORT_TEST')
MAPISTO_DB_PASSWORD_TEST = os.environ.get('MAPISTO_DB_PASSWORD_TEST')
