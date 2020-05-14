from resources.Territory import Territory
from .conversion import path_to_polygon
def territories_conflict(a, b):
    assert isinstance(a, Territory)
    assert isinstance(b, Territory)
    assert a.representations[0].precision_in_km == 0
    assert b.representations[0].precision_in_km == 0

    a_polygon = path_to_polygon(a.representations[0].d_path)
    b_polygon = path_to_polygon(b.representations[0].d_path)
    
    return a_polygon.intersection(b_polygon).area > 0