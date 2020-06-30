from resources.BoundingBox import BoundingBox
import functools
import conf
def precision_from_bbox_and_px_width(bbox, pixel_width):
    assert isinstance(bbox, BoundingBox)
    km_per_pt= 1100/40000 * bbox.width
    required_precision = .5*km_per_pt
    return functools.reduce(lambda prev,curr : curr if abs(curr - required_precision) < abs(prev - required_precision) else prev , conf.PRECISION_LEVELS )
