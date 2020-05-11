from datetime import datetime
from StateTag import StateTag
from resources.State import State
from werkzeug.exceptions import Conflict
import pytest

def test_add_state():
    to_add = State.from_dict({
        'validity_start' : '1919-01-24T00:23:00Z',
        'validity_end' : '1924-01-01T00:00:00Z',
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

