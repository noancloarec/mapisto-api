from svgpath2mpl import parse_path
from shapely.geometry import Polygon
from math import floor, ceil

def get_bounding_box(path):
    minx, miny, maxx, maxy = Polygon(parse_path(path).to_polygons()[0]).bounds
    # As the coordinates of the polygon will be rounded, the bounding box is stretched to the next integer-coordinates bounding box
    return ( floor(minx), floor(miny), ceil(maxx), ceil(maxy) )
