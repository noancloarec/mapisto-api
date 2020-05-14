from resources.Territory import Territory
from .consistency import territories_conflict


# see consistency_test_set.svg to visualize the polygons
# see consistency_test.ggb to edit the test set with geogebra

#  The green square at origin 
existing_pol = "M 0 1 L 0 0 L 1 0 L 1 1 Z"
candidate_not_touching = "M 1 2.7 L 1.7 2 L 2 3 Z"
candidate_intersection_1_polygon="M 2 1 L 2 0 L 0.5 0.5 Z"
candidate_intersection_1_line="M 0.5 -1 L 0 -0.5 L 0.33 0 L 0.73 0 Z"
candidate_intersection_2_lines="M 0.17 1.34 L 0.28 1 L 0.78 1 L -0.18 2.06 L -0.6 0.39 L 0 0.3 L 0 0.72 L -0.22 1.27 Z"

# The green square on the right top
second_existing_pol="M 4 4 L 4 3 L 5 3 L 5 4 Z"
candidate_intersection_2_polygons="M 3 3 L 4.2 3.2 L 3.6 3.6 L 4.2 3.8 L 3 4 Z"
candidate_intersection_1_shared_point="M 4 5 L 4.5 4 L 4.5 5 Z"
candidate_intersection_1_line_and_1_point="M  5.5 5 L 5 3.82 L 5.76 3.59 L 5 3.5 L 5 3.16 L 6 3 Z"
candidate_intersection_1_line_and_1_polygon="M 4 2.5 L 4.21 3 L 4.41 3 L 4.5 2.5 L 4.69 3.15 L 5 2.5 L 4.5 2 Z"

def to_territory(svg_path):
    return Territory.from_dict({
        'd_path' : svg_path,
        'state_id' : 12, 
        'color' : '#FF0000', 
        'validity_start' : '1918-01-01T00:00:00Z',
        'validity_end' : '1919-01-01T00:00:00Z',
        'name' : 'Algeria'
        }
    )

first_existing_terr = to_territory(existing_pol)
def test_conflict_no_intersection():
    assert territories_conflict(first_existing_terr, to_territory(candidate_not_touching)) is False

def test_conflict_basic_intersection():
    assert territories_conflict(first_existing_terr, to_territory(candidate_intersection_1_polygon)) is True

def test_conflict_line_intersection():
    assert territories_conflict(first_existing_terr, to_territory(candidate_intersection_1_line)) is False

def test_conflict_2_lines_intersection():
    assert territories_conflict(first_existing_terr, to_territory(candidate_intersection_2_lines)) is False

second_existing_terr = to_territory(second_existing_pol)

def test_conflict_2_polygons_intersection():
    assert territories_conflict(second_existing_terr, to_territory(candidate_intersection_2_polygons)) is True

def test_conflict_intersection_is_point():
    assert territories_conflict(second_existing_terr, to_territory(candidate_intersection_1_shared_point)) is False

def test_conflict_intersection_is_line_and_point():
    assert territories_conflict(second_existing_terr, to_territory(candidate_intersection_1_line_and_1_point)) is False

def test_conflict_intersection_is_line_and_pol():
        assert territories_conflict(second_existing_terr, to_territory(candidate_intersection_1_line_and_1_polygon)) is True



