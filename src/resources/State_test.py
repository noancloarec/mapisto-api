from .State import State
from .StateRepresentation import StateRepresentation
import pytest
from dateutil.parser import parse
from werkzeug.exceptions import BadRequest
state_dict = {
    'validity_start' : '1919-01-24T00:23:00Z',
    'validity_end' : '1924-01-01T00:00:00Z',
}

def state_with_representations(state_dict, representations_array):
    res = dict()
    res.update(state_dict)
    res.update({"representations" : representations_array})
    return res

def test_from_dict_1_valid_representations_with_name():
    rpz = [{
        'name' : 'Michel',
        'validity_start' : '1919-01-24T00:23:00Z',
        'validity_end' : '1924-01-01T00:00:00Z',
        'color' : '#FFFFFF'
    }]
    s = State.from_dict(state_with_representations(state_dict, rpz))
    assert isinstance(s, State)
    assert s.validity_start==parse(state_dict['validity_start']).replace(tzinfo=None)
    assert len(s.representations) == len(rpz)

def test_date_are_without_tz():
    rpz = [{
        'name' : 'Michel',
        'validity_start' : '1919-01-24T00:23:00Z',
        'validity_end' : '1924-01-01T00:00:00Z',
        'color' : '#FFFFFF'
    }]
    s = State.from_dict(state_with_representations(state_dict, rpz))
    assert s.validity_start.tzinfo is None
    assert s.validity_end.tzinfo is None
    assert s.representations[0].validity_start.tzinfo is None
    assert s.representations[0].validity_end.tzinfo is None
    assert s.validity_start.isoformat() == state_dict['validity_start'].replace('Z', '')
    assert s.validity_end.isoformat() == state_dict['validity_end'].replace('Z', '')
    assert s.representations[0].validity_start.isoformat() == rpz[0]['validity_start'].replace('Z', '')
    assert s.representations[0].validity_end.isoformat() == rpz[0]['validity_end'].replace('Z', '')
    

def test_name_is_stripped():
    rpz = [{
        'name' : 'Michel ',
        'validity_start' : '1919-01-24T00:23:00Z',
        'validity_end' : '1924-01-01T00:00:00Z',
        'color' : '#FFFFFF'
    }]
    s = State.from_dict(state_with_representations(state_dict, rpz))
    assert s.representations[0].name=='Michel'

def test_from_dict_1_valid_representations_empty_name():
    rpz = [{
        'name' : '',
        'validity_start' : '1919-01-24T00:23:00Z',
        'validity_end' : '1924-01-01T00:00:00Z',
    }]
    # Should accept empty name and no color
    State.from_dict(state_with_representations(state_dict, rpz))

def test_from_dict_1_wrong_representation_date_inversed():
    rpz = [{
        'name' : '',
        'validity_end' : '1919-01-24T00:23:00Z',
        'validity_start' : '1924-01-01T00:00:00Z',
    }]
    with pytest.raises(BadRequest):
        State.from_dict(state_with_representations(state_dict, rpz))
def test_from_dict_1_wrong_representation_date_do_not_cover():
    rpz = [{
        'name' : '',
        'validity_start' : '1919-01-24T00:23:00Z',
        'validity_end' : '1923-01-12T00:00:00Z',
    }]
    with pytest.raises(BadRequest):
        State.from_dict(state_with_representations(state_dict, rpz))

def test_from_dict_1_wrong_representation_date_is_too_wide():
    rpz = [{
        'name' : '',
        'validity_start' : '1919-01-24T00:23:00Z',
        'validity_end' : '1924-01-12T00:00:00Z',
    }]
    with pytest.raises(BadRequest):
        State.from_dict(state_with_representations(state_dict, rpz))

def test_from_dict_2_representation_date_ok():
    rpz = [{
        'name' : '',
        'validity_start' : '1919-01-24T00:23:00Z',
        'validity_end' : '1920-01-01T00:00:00Z',
    },
    {
        'name' : '',
        'validity_start' : '1920-01-01T00:00:00Z',
        'validity_end' : '1924-01-01T00:00:00Z',
    }
    ]
    State.from_dict(state_with_representations(state_dict, rpz))
def test_from_dict_2_representation_date_too_wide():
    rpz = [{
        'name' : '',
        'validity_start' : '1919-01-24T00:23:00Z',
        'validity_end' : '1920-01-01T00:00:00Z',
    },
    {
        'name' : '',
        'validity_start' : '1920-01-01T00:00:00Z',
        'validity_end' : '1924-01-01T01:00:00Z', # 1 hour too late
    }
    ]
    with pytest.raises(BadRequest):
        State.from_dict(state_with_representations(state_dict, rpz))

def test_from_dict_2_representation_empty_time_between():
    rpz = [{
        'name' : '',
        'validity_start' : '1919-01-24T00:23:00Z',
        'validity_end' : '1920-01-01T00:00:00Z',
    },
    {
        'name' : '',
        'validity_start' : '1920-01-01T00:00:01Z', # 1 second too late
        'validity_end' : '1924-01-01T00:00:00Z',
    }
    ]
    with pytest.raises(BadRequest):
        State.from_dict(state_with_representations(state_dict, rpz))

def test_from_dict_2_representation_period_intersects():
    rpz = [{
        'name' : '',
        'validity_start' : '1919-01-24T00:23:00Z',
        'validity_end' : '1920-01-01T00:00:01Z',
    },
    {
        'name' : '',
        'validity_start' : '1920-01-01T00:00:00Z', # 1 second too soon
        'validity_end' : '1924-01-01T00:00:00Z',
    }
    ]
    with pytest.raises(BadRequest):
        State.from_dict(state_with_representations(state_dict, rpz))

