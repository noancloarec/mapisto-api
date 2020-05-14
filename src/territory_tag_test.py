from territory_tag import TerritoryTag
from shapely.geometry import Polygon
from resources.Territory import Territory
from resources.State import State
from random import randint
from maps_geometry.conversion import path_to_polygon, to_svg_path
from state_tag import StateTag
from shapely.affinity import translate
from datetime import datetime
import pytest
from werkzeug.exceptions import Conflict, NotFound
import conf


def get_example_state():
    return   State.from_dict({
        'validity_start' : '1918-01-01T00:00:00Z',
        'validity_end' : '1919-01-01T00:00:00Z',
        'representations' : [
            {
            'name' :  'test ' + datetime.now().isoformat()+ str(randint(1,1e6)),
            'validity_start' : '1918-01-01T00:00:00Z',
            'validity_end' : '1919-01-01T00:00:00Z',
            }
        ]
    })


example_territory = Territory.from_dict({
        'd_path' : "M 0 1 L 0 0 L 1 0 L 1 1 Z",
        'state_id' : 12, 
        'color' : '#FF0000', 
        'validity_start' : '1918-01-01T00:00:00Z',
        'validity_end' : '1919-01-01T00:00:00Z',
        'name' : 'Algeria'
        }
    )

def translate_terr(a, dx, dy):
    pol = path_to_polygon(a.representations[0].d_path)
    assert isinstance(pol, Polygon)
    a.representations[0].d_path = to_svg_path(translate(pol, dx, dy))


def test_post_territory_nominal():
    state_id = StateTag.post(get_example_state())
    translate_terr(example_territory, datetime.now().timestamp(), datetime.now().timestamp())
    example_territory.state_id=state_id
    territory_id = TerritoryTag.post(example_territory)
    assert isinstance(territory_id, int)
    retrieved = TerritoryTag.get(territory_id)
    assert len(retrieved.representations) > 1

def test_post_territory_state_conflict_on_period():
    example_state = get_example_state()
    example_state.representations[0].name = 'test ' + datetime.now().isoformat()+' a'
    state_id=StateTag.post(example_state)
    example_territory.validity_end.replace(year=example_territory.validity_end.year+1)
    example_territory.state_id = state_id
    with pytest.raises(Conflict):
        TerritoryTag.post(example_territory)

def test_post_territory_conflict_on_geography():
    example_state=get_example_state()
    state_id = StateTag.post(example_state)
    translate_terr(example_territory, datetime.now().timestamp()+12, datetime.now().timestamp()+12)
    example_territory.state_id=state_id
    TerritoryTag.post(example_territory)
    with pytest.raises(Conflict):
        TerritoryTag.post(example_territory)

def test_post_territory_state_does_not_exist():
    translate_terr(example_territory, datetime.now().timestamp()+45, datetime.now().timestamp()+45)
    example_territory.state_id=-1
    with pytest.raises(NotFound):
        TerritoryTag.post(example_territory)






