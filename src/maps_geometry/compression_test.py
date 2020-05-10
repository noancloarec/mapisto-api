from .compression import get_point_precision, to_svg_path, path_to_polygon, compress, compress_land
from shapely.geometry import Polygon
from resources.Land import Land
from resources.MapistoShape import MapistoShape
from resources.BoundingBox import BoundingBox

test_polygon = Polygon([(0.1,0), (10.12, 10), (0, 15.7),(-2, 7), (-3, 6), (-5, 0)])
test_path = "M 0.1 0 L 10.12 10 L 0 15.7 L -2 7 L -3 6 L -5 0 Z"

def test_get_point_precision():
    assert isinstance(get_point_precision(1000.5), float)
    assert get_point_precision(0) == 0.0

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
    assert isinstance(compress(test_path, 2), str)
    assert compress(test_path, 48) is None
    assert len(compress(test_path, 3)) < len(test_path)
    assert "0.1" not in compress(test_path, 1)
    assert "0.1" in compress(test_path, .05)

def test_compress_land():
    example_land = Land(12, [MapistoShape(test_path, 0)], BoundingBox(0,0,100,100))
    compressed = compress_land(example_land)
    assert isinstance(compressed, Land)
    assert isinstance(compressed.representations, list)
    assert len(compressed.representations) > 0
    assert compressed.representations[0].precision_in_km == 0 # 0 is raw precision
    for i, rep in enumerate(compressed.representations):
        assert isinstance(rep, MapistoShape)
        if i > 0:
            previous = compressed.representations[i-1]
            # Assumes precision_levels is sorted asc
            assert rep.precision_in_km > previous.precision_in_km #representations are sorted by precision asc
            assert previous.precision_in_km==0 or len(rep.d_path) <= len(previous.d_path) # Precision asc means size desc (as more precise = bigger definition)
