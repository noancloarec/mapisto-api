from .db import get_cursor
from .State_CRUD import StateCRUD
from .Territory_CRUD import TerritoryCRUD, Territory
from resources.State import State
from resources.StateRepresentation import StateRepresentation
from .db import get_cursor
from werkzeug.exceptions import NotFound
import pytest
from resources.BoundingBox import BoundingBox
from werkzeug.exceptions import Conflict
import copy
import contextlib
import psycopg2.errors

from datetime import datetime
from dateutil import parser
example_state = State.from_dict({
    'validity_start' : '1919-01-24T00:23:00Z',
    'validity_end' : '1924-01-01T00:00:00Z',
    'representations' : [
        {
        'name' : 'Austria',
        'validity_start' : '1919-01-24T00:23:00Z',
        'validity_end' : '1920-01-01T00:00:00Z',
        },
        {
            'name' : '',
            'validity_start' : '1920-01-01T00:00:00Z',
            'validity_end' : '1924-01-01T00:00:00Z',
        }
    ]
})

def test_get_state_not_found():
    with get_cursor() as curs:
        with pytest.raises(NotFound):
            StateCRUD.get(curs, -12)

def test_add_and_get_state():
    with get_cursor() as curs:
        old_count = StateCRUD.count(curs)
        state_id = StateCRUD.add(curs, example_state)
        assert isinstance(state_id, int)
        
    with get_cursor() as curs:
        retrieved = StateCRUD.get(curs, state_id)
        assert isinstance(retrieved, State)
        retrieved.state_id=None
        print('retrieved : ', retrieved)
        print(retrieved.validity_start.tzinfo)
        print(example_state.validity_start.tzinfo)
        print(retrieved.validity_start==example_state.validity_start)
        print('example : ', example_state)
        
        assert retrieved.equals(example_state)
        assert StateCRUD.count(curs) == old_count+1

def test_count_states():
    with get_cursor() as curs:
        assert isinstance(StateCRUD.count(curs), int)

def test_add_corrupted_state():
    corrupted_state = copy.deepcopy(example_state)
    corrupted_state.representations[0].validity_start='Audrey Tautou'
    with get_cursor() as curs:
        old_nb_states = StateCRUD.count(curs)
    with get_cursor() as curs:
        with pytest.raises(Exception):
            StateCRUD.add(curs, corrupted_state)
    with get_cursor() as curs:
        assert StateCRUD.count(curs)==old_nb_states # no land was added

def test_search_states():
    pass


def year_to_date(y):
    return parser.parse(f'{y}-01-01T00:00:00Z')

france_2012_2018 = State.from_dict({
    'validity_start' : year_to_date(2012).isoformat(),
    'validity_end' : year_to_date(2018).isoformat(),
    'representations' : [
        {
        'name' : 'France',
        'validity_start' : year_to_date(2012).isoformat(),
        'validity_end' : '2015-02-02T00:00:00Z',
        },
        {
        'name' : 'france with other name',
        'validity_start' : '2015-02-02T00:00:00Z',
        'validity_end' : '2015-02-03T00:00:00Z',
        },
        {
        'name' : 'France',
        'validity_start' : '2015-02-03T00:00:00Z',
        'validity_end' : year_to_date(2018).isoformat(),
        },
    ]
})



def test_delete_state():
    with get_cursor() as curs:
        state_id = StateCRUD.add(curs, example_state)
        count = StateCRUD.count(curs)
        StateCRUD.delete(curs, state_id)
        assert StateCRUD.count(curs)==count-1

@contextlib.contextmanager
def get_db_with_states_cursor(*states):
    with get_cursor() as curs :
        state_ids = [StateCRUD.add(curs, state) for state in states]
        yield curs
        for state_id in state_ids:
            StateCRUD.delete(curs, state_id)

def test_get_by_name_case_insensitive():
    with get_db_with_states_cursor(france_2012_2018) as cursor:
        res = StateCRUD.get_by_name(cursor, 'frAnce', year_to_date(2012), year_to_date(2018))
        assert len(res) >= 1
        assert any(st.equals(france_2012_2018) for st in res)

def test_get_by_name_when_no_france():
    with get_db_with_states_cursor(france_2012_2018) as cursor:
        res = StateCRUD.get_by_name(cursor, 'frAnce', parser.parse('2015-02-02T00:00:00Z'), parser.parse('2015-02-02T01:00:00Z')) # france does not exist at this specific time
        # so nothing should be found
        assert not any(st.equals(france_2012_2018) for st in res)

def test_get_by_name_too_late():
    with get_db_with_states_cursor(france_2012_2018) as cursor:
        res = StateCRUD.get_by_name(cursor, 'frAnce', year_to_date(2018), year_to_date(2020))
        assert not any(st.equals(france_2012_2018) for st in res)

def test_get_by_name_period_intersects_end():
    with get_db_with_states_cursor(france_2012_2018) as cursor:
        res = StateCRUD.get_by_name(cursor, 'frAnce', year_to_date(2013), year_to_date(2020))
        assert any(st.equals(france_2012_2018) for st in res)

def test_get_by_name_period_intersects_start():
    with get_db_with_states_cursor(france_2012_2018) as cursor:
        res = StateCRUD.get_by_name(cursor, 'frAnce', year_to_date(2001), year_to_date(2013))
        assert any(st.equals(france_2012_2018) for st in res)

def test_get_by_name_several_matches():
    france_2001_2003 = State.from_dict({
        'validity_start' : year_to_date(2001).isoformat(),
        'validity_end' : year_to_date(2003).isoformat(),
        'representations' : [
            {
            'name' : 'France',
            'validity_start' : year_to_date(2001).isoformat(),
            'validity_end' : year_to_date(2003).isoformat(),
            },
        ]
    })
    with get_db_with_states_cursor(france_2012_2018, france_2001_2003) as cursor:
        res = StateCRUD.get_by_name(cursor, 'frAnce', year_to_date(2002), year_to_date(2015))
        assert len(res) >= 2
        assert any(st.equals(france_2012_2018) for st in res)
        assert any(st.equals(france_2001_2003) for st in res)

def test_get_bbox_no_territories():
    with get_cursor() as curs:
        state_id = StateCRUD.add(curs, france_2012_2018)
        try :
            with pytest.raises(NotFound):
                StateCRUD.get_bbox(curs, state_id, year_to_date(2013))
        finally :
            StateCRUD.delete(curs, state_id)

def test_get_bbox_no_state():
    with get_cursor() as curs:
        with pytest.raises(NotFound):
            StateCRUD.get_bbox(curs, -1, year_to_date(2014))
