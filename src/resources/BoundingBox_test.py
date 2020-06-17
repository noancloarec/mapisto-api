from .BoundingBox import BoundingBox

def test_enlarge_to_ratio_ratio_ok():
    bbox = BoundingBox(0, 0, 1, 1)
    ratio = 16/9
    enlarged = bbox.enlarge_to_aspect_ratio(ratio)
    assert enlarged.width/enlarged.height == ratio

def test_enlarge_ratio_original_is_contained():
    bbox = BoundingBox(4,2, 12, 1)
    ratio = 16/9
    enlarged = bbox.enlarge_to_aspect_ratio(ratio)
    assert enlarged.union(bbox).equals(enlarged)

def test_enlarge_ratio_center_remains_the_same():
    bbox = BoundingBox(4,2, 12, 1)
    ratio = 16/9
    enlarged = bbox.enlarge_to_aspect_ratio(ratio)
    assert enlarged.center() == bbox.center()
