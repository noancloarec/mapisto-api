import conf
import psycopg2
import contextlib
@contextlib.contextmanager
def get_cursor():
    with _create_connection() as conn:
        yield conn.cursor()
        
def _create_connection():
    return psycopg2.connect(
        database=conf.MAPISTO_DB_NAME,
        user=conf.MAPISTO_DB_USER,
        password=conf.MAPISTO_DB_PASSWORD,
        host=conf.MAPISTO_DB_HOST,
        port=conf.MAPISTO_DB_PORT,
        options='-c search_path=mapisto')

