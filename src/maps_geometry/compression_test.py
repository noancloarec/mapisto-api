from .compression import _get_point_precision, _compress, compress_land, compress_territory
from .conversion import to_svg_path, path_to_polygon
from shapely.geometry import Polygon
from resources.Land import Land
from resources.Territory import Territory
from resources.MapistoShape import MapistoShape
from datetime import datetime
from resources.BoundingBox import BoundingBox

test_polygon = Polygon(
    [(0.1, 0), (10.12, 10), (0, 15.7), (-2, 7), (-3, 6), (-5, 0)])
test_path = "M 0.1 0 L 10.12 10 L 0 15.7 L -2 7 L -3 6 L -5 0 Z"


def test_get_point_precision():
    assert isinstance(_get_point_precision(1000.5), float)
    assert _get_point_precision(0) == 0.0


def test_to_svg_path():
    path = to_svg_path(test_polygon)
    assert isinstance(path, str)
    assert len(path)
    assert path_to_polygon(path).equals(test_polygon)


def test_path_to_polygon():
    pol = path_to_polygon(test_path)
    assert isinstance(pol, Polygon)
    print(pol)
    print(test_polygon)
    assert pol.equals(test_polygon)


def test_compress():
    assert isinstance(_compress(test_path, 2), str)
    assert _compress(test_path, 48) is None
    assert len(_compress(test_path, 3)) < len(test_path)
    assert "0.1" not in _compress(test_path, 1)
    assert "0.1" in _compress(test_path, .05)


def test_compress_land():
    example_land = Land(12, [MapistoShape(test_path, 0)],
                        BoundingBox(0, 0, 100, 100))
    compressed = compress_land(example_land)
    assert isinstance(compressed, Land)
    assert isinstance(compressed.representations, list)
    assert len(compressed.representations) > 0
    # 0 is raw precision
    assert compressed.representations[0].precision_in_km == 0
    for i, rep in enumerate(compressed.representations):
        assert isinstance(rep, MapistoShape)
        if i > 0:
            previous = compressed.representations[i-1]
            # Assumes precision_levels is sorted asc
            # representations are sorted by precision asc
            assert rep.precision_in_km > previous.precision_in_km
            # Precision asc means size desc (as more precise = bigger definition)
            assert previous.precision_in_km == 0 or len(
                rep.d_path) <= len(previous.d_path)


def test_compress_territory():
    example_territory = Territory(12,
                                  representations=[MapistoShape(test_path, 0)],
                                  bounding_box=BoundingBox(0, 0, 100, 100),
                                  state_id=14,
                                  validity_start=datetime.now(),
                                  validity_end=datetime.now(),
                                  color='#FF0000',
                                  name="Algeria")
    compressed = compress_territory(example_territory)
    assert isinstance(compressed, Territory)
    # 0 is raw precision
    assert compressed.representations[0].precision_in_km == 0
    for i, rep in enumerate(compressed.representations):
        assert isinstance(rep, MapistoShape)
        if i > 0:
            previous = compressed.representations[i-1]
            # Assumes precision_levels is sorted asc
            # representations are sorted by precision asc
            assert rep.precision_in_km > previous.precision_in_km
            # Precision asc means size desc (as more precise = bigger definition)
            assert previous.precision_in_km == 0 or len(
                rep.d_path) <= len(previous.d_path)
    compressed.representations = [compressed.representations[0]]
    assert compressed.equals(example_territory)