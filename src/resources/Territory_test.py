from .Territory import Territory
import pytest
from werkzeug.exceptions import BadRequest
from datetime import datetime

territory_dict = {
    'd_path' : "M 0.1 0 L 10.12 10 L 0 15.7 L -2 7 L -3 6 L -5 0 Z",
    'state_id' : 12, 
    'color' : '#FF0000', 
    'validity_start' : '1918-01-01T00:00:00Z',
    'validity_end' : '1919-01-01T00:00:00Z',
    'name' : 'Algeria'
}
partial_territory_ok = {
    'd_path' : "M 0.1 0 L 10.12 10 L 0 15.7 L -2 7 L -3 6 L -5 0 Z",
    'state_id' : 12, 
    'validity_start' : '1918-01-01T00:00:00Z',
    'validity_end' : '1919-01-01T00:00:00Z',
}
partial_territory_pa_ok = {
    'd_path' : "M 0.1 0 L 10.12 10 L 0 15.7 L -2 7 L -3 6 L -5 0 Z",
    'validity_start' : '1918-01-01T00:00:00Z',
    'validity_end' : '1919-01-01T00:00:00Z',
}
def test_territory_from_dict():
    t = Territory.from_dict(territory_dict)
    assert isinstance(t, Territory)
    
def test_partial_territory_ok():
    t = Territory.from_dict(partial_territory_ok)
    assert isinstance(t, Territory)
    assert t.color is None
    assert t.name is None

def test_partial_territory_not_ok():
    with pytest.raises(BadRequest):
        Territory.from_dict(partial_territory_pa_ok)

def test_territory_to_dict():
    terr = Territory.from_dict(territory_dict)
    as_dict = terr.to_dict()
    assert as_dict['name'] == 'Algeria'
    assert isinstance(as_dict['validity_start'], datetime)