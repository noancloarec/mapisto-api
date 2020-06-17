from map_tag import MapTag
import conf
from resources.BoundingBox import BoundingBox
from dateutil import parser
from resources.Territory import Territory
from resources.State import State
from werkzeug.exceptions import NotFound


def year_to_date(y):
    return parser.parse(f'{y}-01-01T00:00:00Z').replace(tzinfo=None)



def test_get_map():
    bbox = BoundingBox(0, 0, 1116, 11114)
    res = MapTag.get(bbox, year_to_date(1918), max(conf.PRECISION_LEVELS)) 
    ensure_is_map_data(res)

def test_get_state_map():
    try :
        res = MapTag.get_by_state(24, year_to_date(1850), max(conf.PRECISION_LEVELS))
        ensure_is_map_data(res)
        assert isinstance(res['bounding_box'], BoundingBox)
    except NotFound:
        pass

def ensure_is_map_data(server_result):
    assert isinstance(server_result, dict)
    assert isinstance(server_result['states'], list)
    assert isinstance(server_result['territories'], list)

    for st in server_result['states']:
        assert isinstance(st, State)
    st_ids = [st.state_id for st in server_result['states']]
    for t in server_result['territories']:
        assert isinstance(t, Territory)
        assert not t.is_outdated(year_to_date(1918))
        assert t.state_id in st_ids
