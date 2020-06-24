from resources.Territory import Territory
from .Territory_CRUD import TerritoryCRUD
from resources.State import State
from .State_CRUD import StateCRUD
import contextlib
from dateutil import parser
from .db import get_cursor
import pytest
from werkzeug.exceptions import NotFound
from resources.BoundingBox import BoundingBox

algeria = Territory.from_dict({
    # bounding box -5 , 0, 16, 16
    'd_path': "M 0.1 0 L 10.12 10 L 0 15.7 L -2 7 L -3 6 L -5 0 Z",
    'state_id': 12,
    'validity_start': '1918-01-01T00:00:00Z',
    'validity_end': '1919-01-01T00:00:00Z',
    'name': 'Algeria'
})
corsica = Territory.from_dict({
    # bounding box -5 , 10, 16, 16
    'd_path': "M 0.1 10 L 10.12 20 L 0 25.7 L -2 17 L -3 16 L -5 10 Z",
    'state_id': 12,
    'validity_start': '1916-01-01T00:00:00Z',
    'validity_end': '1919-01-01T00:00:00Z',
    'name': 'Corsica'
})


def year_to_date(y):
    return parser.parse(f'{y}-01-01T00:00:00Z')


france_1912_2018 = State.from_dict({
    'validity_start': year_to_date(1912).isoformat(),
    'validity_end': year_to_date(2018).isoformat(),
    'representations': [
        {
            'name': 'France',
            'validity_start': year_to_date(1912).isoformat(),
            'validity_end': '2015-02-02T00:00:00Z',
        },
        {
            'name': 'france with other name',
            'validity_start': '2015-02-02T00:00:00Z',
            'validity_end': '2015-02-03T00:00:00Z',
        },
        {
            'name': 'France',
            'validity_start': '2015-02-03T00:00:00Z',
            'validity_end': year_to_date(2018).isoformat(),
        },
    ]
})


@contextlib.contextmanager
def get_db_with_states_cursor(*states):
    with get_cursor() as curs:
        state_ids = [StateCRUD.add(curs, state) for state in states]
        yield curs
        for state_id in state_ids:
            StateCRUD.delete(curs, state_id)


def test_add_and_get():
    with get_db_with_states_cursor(france_1912_2018) as cursor:
        old_count = TerritoryCRUD.count(cursor)
        france_id = StateCRUD.get_by_name(
            cursor, 'France', france_1912_2018.validity_start, france_1912_2018.validity_end)[0].state_id
        algeria.state_id = france_id
        terr_id = TerritoryCRUD.add(cursor, algeria)
        assert isinstance(terr_id, int)
        assert TerritoryCRUD.count(cursor) == old_count+1
        retrieved = TerritoryCRUD.get(cursor, terr_id)
        assert isinstance(retrieved, Territory)
        assert isinstance(retrieved.territory_id, int)
        assert retrieved.territory_id > 0
        print('source', algeria)
        print('retrieved', retrieved)
        assert retrieved.equals(algeria)


def test_get_404():
    with pytest.raises(NotFound):
        with get_cursor() as cursor:
            TerritoryCRUD.get(cursor, -1)


def test_count():
    with get_cursor() as cursor:
        assert isinstance(TerritoryCRUD.count(cursor), int)


def test_add_state_not_found():
    with pytest.raises(NotFound):
        with get_cursor() as cursor:
            algeria.state_id = -1
            TerritoryCRUD.add(cursor, algeria)


@contextlib.contextmanager
def get_db_with_state_and_territories_cursor(state, *territories):
    with get_cursor() as cursor:
        state_id = StateCRUD.add(cursor, state)
        for t in territories:
            t.state_id = state_id
            TerritoryCRUD.add(cursor, t)
        yield cursor
        StateCRUD.delete(cursor, state_id)  # cascade delete


def test_get_bbox_at_nominal():
    with get_db_with_state_and_territories_cursor(france_1912_2018, algeria, corsica) as cursor:
        bbox = BoundingBox(-20, -2, 16, 14)
        print('alegeria bbox : ', algeria.bounding_box)
        print('corsica bbox : ', corsica.bounding_box)
        date = year_to_date(1918)
        res = TerritoryCRUD.get_within_bbox_at_time(cursor, bbox, date, 0)
        assert isinstance(res, list)
        assert len(res) >= 2
        assert any(t.equals(corsica) for t in res)
        assert any(t.equals(algeria) for t in res)


def test_get_bbox_at_date_limit():
    with get_db_with_state_and_territories_cursor(france_1912_2018, algeria, corsica) as cursor:
        bbox = BoundingBox(-20, -2, 16, 14)
        date = year_to_date(1919)
        res = TerritoryCRUD.get_within_bbox_at_time(cursor, bbox, date, 0)
        assert not any(t.equals(corsica) or t.equals(algeria) for t in res)
        date = year_to_date(1918)
        res = TerritoryCRUD.get_within_bbox_at_time(cursor, bbox, date, 0)
        assert any(t.equals(corsica) for t in res)
        assert any(t.equals(algeria) for t in res)


def test_get_bbox_only_1_retrieved():
    with get_db_with_state_and_territories_cursor(france_1912_2018, algeria, corsica) as cursor:
        bbox = BoundingBox(-20, 17, 16, 4)  # algeria goes till y=16
        date = year_to_date(1918)
        res = TerritoryCRUD.get_within_bbox_at_time(cursor, bbox, date, 0)
        assert any(t.equals(corsica) for t in res)
        assert not any(t.equals(algeria) for t in res)


def test_get_bbox_in_period_nominal():
    with get_db_with_state_and_territories_cursor(france_1912_2018, algeria, corsica) as cursor:
        bbox = BoundingBox(-20, -2, 16, 14)
        res = TerritoryCRUD.get_within_bbox_in_period(
            cursor, bbox, year_to_date(1900), year_to_date(1920), 0)
        assert isinstance(res, list)
        assert len(res) >= 2
        assert any(t.equals(corsica) for t in res)
        assert any(t.equals(algeria) for t in res)


def test_edit_territory():
    corsica = Territory.from_dict({
        # bounding box -5 , 10, 16, 16
        'd_path': "M 0.1 10 L 10.12 20 L 0 25.7 L -2 17 L -3 16 L -5 10 Z",
        'state_id': 12,
        'validity_start': '1916-01-01T00:00:00Z',
        'validity_end': '1919-01-01T00:00:00Z',
        'name': 'Corsica'
    })
    with get_db_with_states_cursor(france_1912_2018) as cursor:
        france_id = StateCRUD.get_by_name(
            cursor, 'France', france_1912_2018.validity_start, france_1912_2018.validity_end)[0].state_id
        corsica.state_id = france_id

        corsica_id = TerritoryCRUD.add(cursor, corsica)
        corsica.territory_id = corsica_id
        corsica.color = '#FFFFFF'
        TerritoryCRUD.edit(cursor, corsica)
        retrieved = TerritoryCRUD.get(cursor, corsica_id)
        assert retrieved.color is None
        TerritoryCRUD.edit(cursor, corsica, change_color=True)
        retrieved = TerritoryCRUD.get(cursor, corsica_id)
        assert retrieved.color==corsica.color

