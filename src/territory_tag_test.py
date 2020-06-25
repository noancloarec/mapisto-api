from territory_tag import TerritoryTag
from shapely.geometry import Polygon
from resources.Territory import Territory
from resources.State import State
from random import randint
from maps_geometry.conversion import path_to_polygon, to_svg_path
from state_tag import StateTag
from shapely.affinity import translate
from datetime import datetime
import contextlib
import pytest
from werkzeug.exceptions import Conflict, NotFound, BadRequest
import conf
import logging
from crud.db import get_cursor
from state_tag import StateTag 
from territory_tag import TerritoryTag
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

def test_post_territory_nominal():
    state_id = StateTag.post(get_example_state())
    example_territory = get_example_territory()
    example_territory.state_id = state_id
    territory_id = TerritoryTag.post(example_territory)
    assert isinstance(territory_id, int)
    retrieved = TerritoryTag.get(territory_id)
    assert len(retrieved.representations) > 1
    TerritoryTag.delete(territory_id)
    StateTag.delete(state_id)


def test_post_territory_state_conflict_on_period():
    example_state = get_example_state()
    state_id = StateTag.post(example_state)
    example_territory = get_example_territory()
    example_territory.validity_end = example_territory.validity_end.replace(
        year=example_state.validity_end.year+1)
    example_territory.state_id = state_id
    logging.warning(f'About to put a territory ending in {example_territory.validity_end} to a state ending in {example_state.validity_end}')
    with pytest.raises(Conflict):
        TerritoryTag.post(example_territory)
    StateTag.delete(state_id)


def test_post_territory_conflict_on_geography():
    with get_api_with_state_and_territory() as [(_, territory)]:
        with pytest.raises(Conflict):
            TerritoryTag.post(territory)


def test_post_territory_state_does_not_exist():
    t = get_example_territory()
    t.state_id = -1
    with pytest.raises(NotFound):
        TerritoryTag.post(t)


def test_get_color_for_territory_different_from_territory_to_new_state():
    territory = get_example_territory()
    old_state = get_example_state()
    new_state = get_example_state()
    territory.color = "#FFFFFF"
    new_state.representations[0].color = '#AA0000'
    assert TerritoryTag._get_color_for_territory(
        territory, old_state, new_state) == '#FFFFFF'


def test_get_color_for_territory_different_from_old_state_to_new_state():
    territory = get_example_territory()
    old_state = get_example_state()
    new_state = get_example_state()
    territory.color = None
    old_state.representations[0].color = '#FFFFFF'
    new_state.representations[0].color = '#AAAAAA'
    assert TerritoryTag._get_color_for_territory(
        territory, old_state, new_state) == '#FFFFFF'


def test_get_color_for_territory_color_similar():
    territory = get_example_territory()
    old_state = get_example_state()
    new_state = get_example_state()
    territory.color = '#FEEEEE'
    old_state.representations[0].color = '#000000'
    new_state.representations[0].color = '#EEEEEE'
    assert TerritoryTag._get_color_for_territory(
        territory, old_state, new_state) == None


# def test_get_color_for_territory_color_similar_on_first_part_but_different_on_second_part():
#     territory = get_example_territory()
#     old_state = get_example_state()
#     new_state = State.from_dict({
#         'validity_start': '1918-01-01T00:00:00Z',
#         'validity_end': '1919-01-01T00:00:00Z',
#         'representations': [
#             {
#                 'name':  'test ' + datetime.now().isoformat() + str(randint(1, 1e6)),
#                 'validity_start': '1918-01-01T00:00:00Z',
#                 'validity_end': '1918-06-01T00:00:00Z',
#                 'color' : '#FFFFFF' # same as territory color so result could be None
#             },
#             {
#                 'name':  'test ' + datetime.now().isoformat() + str(randint(1, 1e6)),
#                 'validity_start': '1918-06-01T00:00:00Z',
#                 'validity_end': '1919-01-01T00:00:00Z',
#                 'color' : '#999999' # different than territory color so result will be FFFFFF (initial territory color)
#             }
#         ]
#     })    
#     territory.color = '#FFFFFF'
#     new_state.representations[0].color = '#EEEEEE'
    # assert TerritoryTag._get_color_for_territory(territory, old_state, new_state) == "#FFFFFF"

def test_assign_to_state_with_unmatching_period():
    state1 = State.from_dict({
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
    state2 = State.from_dict({
        'validity_start': '1919-01-01T00:00:00Z',
        'validity_end': '1920-01-01T00:00:00Z',
        'representations': [
            {
                'name':  'test ' + datetime.now().isoformat() + str(randint(1, 1e6)),
                'validity_start': '1919-01-01T00:00:00Z',
                'validity_end': '1920-01-01T00:00:00Z',
                'color' : '#000000'
            }
        ]
    })
    territory = get_example_territory()

    # state2 and territory have no period in common
    with get_api_with_state_and_territory((state1, territory), (state2, None)) as [(_, territory_with_id), (state2_w_id, _)]:
        with pytest.raises(BadRequest):
            with get_cursor() as cursor :
                TerritoryTag._assign_to_state(cursor, territory_with_id, state2_w_id.state_id)

def test_assign_to_state_territory_starts_before_new_state():
    state1 = State.from_dict({
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
    state2 = State.from_dict({
        'validity_start': '1918-02-01T00:00:00Z',
        'validity_end': '1919-01-01T00:00:00Z',
        'representations': [
            {
                'name':  'test ' + datetime.now().isoformat() + str(randint(1, 1e6)),
                'validity_start': '1918-02-01T00:00:00Z',
                'validity_end': '1919-01-01T00:00:00Z',
                'color' : '#000000'
            }
        ]
    })
    # territory exists in jan 1918 and state2 does not
    territory = get_example_territory()
    with get_api_with_state_and_territory((state1, territory), (state2, None)) as [(state1_with_id, territory_with_id), (state2_w_id, _)]:
        territory_count = TerritoryTag.count()
        with get_cursor() as cursor :
            created_ids = TerritoryTag._assign_to_state(cursor, territory_with_id, state2_w_id.state_id)
        # a territory was created for jan 1918 and it still belongs to state1
        assert TerritoryTag.count() == territory_count + 1 
        assert len(created_ids) == 1
        assert TerritoryTag.get(created_ids[0]).state_id == state1_with_id.state_id
        
def test_assign_to_state_territory_starts_before_and_ends_after_new_state():
    state1 = State.from_dict({
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
    state2 = State.from_dict({
        'validity_start': '1918-02-01T00:00:00Z',
        'validity_end': '1918-12-01T00:00:00Z',
        'representations': [
            {
                'name':  'test ' + datetime.now().isoformat() + str(randint(1, 1e6)),
                'validity_start': '1918-02-01T00:00:00Z',
                'validity_end': '1918-12-01T00:00:00Z',
                'color' : '#000000'

            }
        ]
    })
    # territory exists in jan and dec 1918 and state2 does not
    territory = get_example_territory()
    with get_api_with_state_and_territory((state1, territory), (state2, None)) as [(state1_with_id, territory_with_id), (state2_w_id, _)]:
        territory_count = TerritoryTag.count()
        with get_cursor() as cursor :
            created_ids = TerritoryTag._assign_to_state(cursor, territory_with_id, state2_w_id.state_id)
        # 2 territories were created for jan 1918 and it still belongs to state1
        assert TerritoryTag.count() == territory_count + 2
        assert len(created_ids) == 2
        assert all(TerritoryTag.get(created_id).state_id == state1_with_id.state_id for created_id in created_ids)
        
def test_assign_to_state_territory_color_were_preserved():
    state1 = State.from_dict({
        'validity_start': '1918-01-01T00:00:00Z',
        'validity_end': '1919-01-01T00:00:00Z',
        'representations': [
            {
                'name':  'test ' + datetime.now().isoformat() + str(randint(1, 1e6)),
                'validity_start': '1918-01-01T00:00:00Z',
                'validity_end': '1919-01-01T00:00:00Z',
                'color' : '#FF0000' # red
            }
        ]
    })
    state2 = State.from_dict({
        'validity_start': '1918-02-01T00:00:00Z',
        'validity_end': '1918-12-01T00:00:00Z',
        'representations': [
            {
                'name':  'test ' + datetime.now().isoformat() + str(randint(1, 1e6)),
                'validity_start': '1918-02-01T00:00:00Z',
                'validity_end': '1918-12-01T00:00:00Z',
                'color' : '#0000FF' #blue
            }
        ]
    })
    # territory exists in jan and dec 1918 and state2 does not
    territory = get_example_territory()
    territory.color = None # will be red at first
    with get_api_with_state_and_territory((state1, territory), (state2, None)) as [(_, territory_with_id), (state2_w_id, _)]:
        with get_cursor() as cursor :
            created_ids = TerritoryTag._assign_to_state(cursor, territory_with_id, state2_w_id.state_id)

        # The reassigned territory was set to red (so the assign did not change the color)
        assert TerritoryTag.get(territory_with_id.territory_id).color=='#FF0000'
        assert all(TerritoryTag.get(created_id).color == None for created_id in created_ids)
