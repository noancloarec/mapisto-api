from .Land_CRUD import LandCRUD
from .db import get_cursor
from werkzeug.exceptions import NotFound
import pytest
from resources.MapistoShape import MapistoShape
from resources.BoundingBox import BoundingBox
from resources.Land import Land
import copy
import psycopg2.errors

test_path = "M 0.1 0 L 10.12 10 L 0 15.7 L -2 7 L -3 6 L -5 0 Z"
example_land = Land(None, [MapistoShape(test_path, 0)], BoundingBox(-5,0,15,16))

def test_get_land_not_found():
    with get_cursor() as curs:
        with pytest.raises(NotFound):
            LandCRUD.get_land(curs, -12)

def test_add_land():
    with get_cursor() as curs:
        old_count = LandCRUD.count(curs)
        land_id = LandCRUD.add_land(curs, example_land)
        print("ADDED ID : ", land_id)
        
    with get_cursor() as curs:
        retrieved = LandCRUD.get_land(curs, land_id)
        assert isinstance(retrieved, Land)
        retrieved.land_id=None # example land is retrieved but with none
        assert retrieved.equals(example_land)
        assert LandCRUD.count(curs) == old_count+1

def test_count_land():
    with get_cursor() as curs:
        assert isinstance(LandCRUD.count(curs), int)

def test_add_corrupted_land():
    corrupted_land = copy.deepcopy(example_land)
    corrupted_land.representations.append(MapistoShape(test_path, "wrong_precision"))
    with get_cursor() as curs:
        nb_lands_in_db = LandCRUD.count(curs)
    with get_cursor() as curs:
        with pytest.raises(Exception):
            LandCRUD.add_land(curs, corrupted_land)
    with get_cursor() as curs:
        assert LandCRUD.count(curs)==nb_lands_in_db # no land was added