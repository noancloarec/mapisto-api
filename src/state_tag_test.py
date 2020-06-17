from datetime import datetime
from state_tag import StateTag
from resources.State import State
from werkzeug.exceptions import Conflict
import pytest

def test_add_state():
    to_add = State.from_dict({
        'validity_start' : '1919-01-24T00:23:00Z',
        'validity_end' : '1920-01-01T00:00:00Z',
        'representations' : [
            {
            'name' :  'test ' + datetime.now().isoformat(),
            'validity_start' : '1919-01-24T00:23:00Z',
            'validity_end' : '1920-01-01T00:00:00Z',
            }
        ]
    })
    state_id = StateTag.post(to_add)
    assert isinstance(state_id, int)
    with pytest.raises(Conflict):
        StateTag.post(to_add)

def test_add_state_empty_name_no_conflict():
    to_add = State.from_dict({
        'validity_start' : '1919-01-24T00:23:00Z',
        'validity_end' : '1920-01-01T00:00:00Z',
        'representations' : [
            {
            'name' :  '',
            'validity_start' : '1919-01-24T00:23:00Z',
            'validity_end' : '1920-01-01T00:00:00Z',
            }
        ]
    })
    StateTag.post(to_add)
    # should not raise errors
    StateTag.post(to_add)

def test_add_and_get_state() :
    to_add = State.from_dict({
        'validity_start' : '1919-01-24T00:23:00Z',
        'validity_end' : '1920-01-01T00:00:00Z',
        'representations' : [
            {
            'name' :  '',
            'validity_start' : '1919-01-24T00:23:00Z',
            'validity_end' : '1920-01-01T00:00:00Z',
            }
        ]
    })
    st_id = StateTag.post(to_add)
    state = StateTag.get(st_id)
    assert isinstance(state, State)
    assert state.state_id==st_id
    assert state.validity_start==to_add.validity_start
