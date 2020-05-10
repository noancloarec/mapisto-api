from land_tag import LandTag
from crud.db import get_cursor
from crud.Land_CRUD import LandCRUD
from maps_geometry.compression import compress_land
from resources.MapistoShape import MapistoShape
from resources.Land import Land
from werkzeug.exceptions import BadRequest, NotFound
import conf
import pytest
from resources.BoundingBox import BoundingBox

test_path = "M 0.1 0 L 10.12 10 L 0 15.7 L -2 7 L -3 6 L -5 0 Z"
example_land = Land.from_dict({
    'd_path' : test_path
})

def test_post_and_get_land():
    land_id = LandTag.post_land(example_land)
    land = LandTag.get_land(land_id)
    assert land.land_id==land_id
    assert land.representations[0].equals(example_land.representations[0])

def test_post_too_small():
    too_small_land = Land.from_dict({'d_path' : 'M 0 0 L 0.00000001 0.0000002 L 0 0.0000002 Z'})
    with pytest.raises(BadRequest):
        LandTag.post_land(too_small_land)

def test_not_found():
    with pytest.raises(NotFound):
        LandTag.get_land(-1)

def test_get_lands():
    res = LandTag.get_lands(BoundingBox(0,0,4,4), max(conf.PRECISION_LEVELS))
    assert isinstance(res, list)

def test_get_lands_wrong_precision():
    with pytest.raises(BadRequest):
        LandTag.get_lands(BoundingBox(0,0,4,4), max(conf.PRECISION_LEVELS)+1)