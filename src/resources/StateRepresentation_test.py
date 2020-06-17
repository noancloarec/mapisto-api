from .StateRepresentation import StateRepresentation
from datetime import datetime
from dateutil.parser import parse
from werkzeug.exceptions import BadRequest
import pytest
dict_rpz = {
    'name': 'France',
    'validity_start': '1919-01-24T00:23:00Z',
    'validity_end': '1920-01-01T00:00:01Z',
}


def test_from_dict():
    rep = StateRepresentation.from_dict(dict_rpz)
    assert rep.name == 'France'
    assert isinstance(rep.validity_start, datetime)
    assert isinstance(rep.validity_end, datetime)
    assert parse('1919-01-24T00:23:00Z').replace(tzinfo=None) == rep.validity_start

def test_from_dict_bad_date():
    bad_rep = {
    'name': 'France',
    'validity_start': 'Jean friedrich1919-01-24T00:23:00Z',
    'validity_end': '1920-01-01T00:00:01Z',
    }
    with pytest.raises(BadRequest):
        StateRepresentation.from_dict(bad_rep)

def test_to_dict():
    rep = StateRepresentation.from_dict(dict_rpz)
    as_dict = rep.to_dict()
    assert 'color' in as_dict
    assert as_dict['name']=='France'
    assert isinstance(as_dict['validity_start'], datetime)
    assert isinstance(as_dict['validity_end'], datetime)