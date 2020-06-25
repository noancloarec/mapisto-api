from datetime import datetime
from state_tag import StateTag
from resources.State import State
from werkzeug.exceptions import Conflict, NotFound
import pytest
import contextlib
from random import randint
from shapely.geometry import Polygon
from shapely.affinity import translate
from resources.Territory import Territory
from maps_geometry.conversion import path_to_polygon, to_svg_path
from territory_tag import TerritoryTag

def test_add_state():
    to_add = State.from_dict({
        'validity_start' : '1919-01-24T00:23:00Z',
        'validity_end' : '1920-01-01T00:00:00Z',
        'representations' : [
            {
            'name' :  'test ' + datetime.now().isoformat(),
            'validity_start' : '1919-01-24T00:23:00Z',
            'validity_end' : '1920-01-01T00:00:00Z',
            'color' : '#000000'
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
            'color' : '#000000',
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
            'color' : '#000000'
        }
        ]
    })
    st_id = StateTag.post(to_add)
    state = StateTag.get(st_id)
    assert isinstance(state, State)
    assert state.state_id==st_id
    assert state.validity_start==to_add.validity_start
def get_example_state():
    return State.from_dict({
        'validity_start': '1918-01-01T00:00:00Z',
        'validity_end': '1919-01-01T00:00:00Z',
        'representations': [
            {
                'name':  'test ' + datetime.now().isoformat() + str(randint(1, 1e6)),
                'validity_start': '1918-01-01T00:00:00Z',
                'validity_end': '1919-01-01T00:00:00Z',
                'color' : '#000000'
            }
        ]
    })

def get_example_territory():
    territory = Territory.from_dict({
    'd_path': "M 0 1 L 0 0 L 1 0 L 1 1 Z",
    'state_id': 12,
    'color': '#FF0000',
    'validity_start': '1918-01-01T00:00:00Z',
    'validity_end': '1919-01-01T00:00:00Z',
    'name': 'Algeria'})
    offset=datetime.now().timestamp()
    x = offset + randint(1, 1e6)
    y=offset + randint(1, 1e6)
    translate_terr(territory,x, y)
    return territory

def translate_terr(a, dx, dy):
    pol = path_to_polygon(a.representations[0].d_path)
    assert isinstance(pol, Polygon)
    a.representations[0].d_path = to_svg_path(translate(pol, dx, dy))

@contextlib.contextmanager
def get_api_with_state_and_territory(*states_and_territories):
    if not len(states_and_territories):
        states_and_territories = [(get_example_state(),  get_example_territory())]
    for (state, territory) in states_and_territories :
        state_id = StateTag.post(state)
        state.state_id = state_id
        if territory:
            territory.state_id = state_id
            territory_id = TerritoryTag.post(territory)
            territory.territory_id = territory_id

    try :
        yield states_and_territories
    finally: 
        for state, _ in states_and_territories :
           StateTag.delete(state.state_id)

def test_merge_conflict_date_overflows():
    #1918-1919
    sovereign = get_example_state()

    #1917-1919
    to_merge = get_example_state()
    to_merge.validity_start = to_merge.validity_start.replace(year=1917)
    with get_api_with_state_and_territory((sovereign, None), (to_merge,None)) as ((sov_with_id, _), (to_merge_with_id, _)):
        with pytest.raises(Conflict):
            StateTag.merge(to_merge_with_id.state_id, sov_with_id.state_id)


def test_merge_ok():
    #1918-1919
    sovereign = get_example_state()

    #1918-1919
    to_merge = get_example_state()
    t = get_example_territory()
    with get_api_with_state_and_territory((sovereign, None), (to_merge,t)) as ((sov_with_id, _), (to_merge_with_id, t_with_id)):
        StateTag.merge(to_merge_with_id.state_id, sov_with_id.state_id)
        assert TerritoryTag.get(t_with_id.territory_id).state_id == sov_with_id.state_id
        with pytest.raises(NotFound) :
            StateTag.get(to_merge_with_id.state_id)

def test_merge_colors_were_set_from_state():
    sovereign = get_example_state()
    sovereign.representations[0].color='#00000' #black

    to_merge = get_example_state()
    to_merge.representations[0].color = '#FF0000' #red
    t = get_example_territory()
    t.color = None

    with get_api_with_state_and_territory((sovereign, None), (to_merge,t)) as ((sov_with_id, _), (to_merge_with_id, t_with_id)):
        # Territory has the color of its state : red
        assert t_with_id.color==None
        
        #Merge checks the color so they remain consistent
        StateTag.merge(to_merge_with_id.state_id, sov_with_id.state_id)

        t_merged = TerritoryTag.get(t_with_id.territory_id)
        # merge ensured territory remained blue even if its parent is now black
        assert t_merged.color == '#FF0000'
