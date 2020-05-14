from map_tag import MapTag
import conf
from resources.BoundingBox import BoundingBox
from dateutil import parser
from resources.Territory import Territory
from resources.State import State


def year_to_date(y):
    return parser.parse(f'{y}-01-01T00:00:00Z').replace(tzinfo=None)



def test_get_map():
    bbox = BoundingBox(0, 0, 1116, 11114)
    res = MapTag.get(bbox, year_to_date(1918), max(conf.PRECISION_LEVELS)) 
    assert isinstance(res, dict)
    assert isinstance(res['states'], list)
    assert isinstance(res['territories'], list)

    for st in res['states']:
        assert isinstance(st, State)
    st_ids = [st.state_id for st in res['states']]
    for t in res['territories']:
        assert isinstance(t, Territory)
        assert not t.is_outdated(year_to_date(1918))
        assert t.state_id in st_ids



