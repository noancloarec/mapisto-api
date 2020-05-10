from shapely.geometry import Polygon, Point
import xml.etree.ElementTree as ET
from math import floor, log10
import numpy as np
from svgpath2mpl import parse_path
from resources.Land import Land
import conf
from resources.MapistoShape import MapistoShape

SVG_WORLDMAP_WIDTH = 2269.4568
EARTH_WIDTH = 40075
def compress(path, point_precision):
    heavy = path_to_polygon(path)
    light = heavy.simplify(point_precision)
    if light.length < point_precision:
        return None
    if point_precision >= 1 :
        # If precision is bigger than 1 pt, only removes the comma (i.e. no difference between precision 1pt and 1O pt)
        return to_svg_path(Polygon(np.around(light.exterior.coords))).replace('.0', '')
    else :
        # if precision smaller than 1 pts, truncate all coords to n decimals (1 decimal if precision==0.1 , 2 decimals if precision==0.09)
        nb_decimals = - floor(log10(point_precision))
        return to_svg_path(Polygon(np.around(light.exterior.coords, decimals=nb_decimals)))

def get_point_precision(kilometer_precision):
    return SVG_WORLDMAP_WIDTH/EARTH_WIDTH * kilometer_precision

def path_to_polygon(path):
    return Polygon(parse_path(path).to_polygons()[0])

def get_compressed_shapes(rawShape):
    assert isinstance(rawShape, MapistoShape)
    compressed_shapes = [compress(rawShape.d_path, get_point_precision(km_precision)) for km_precision in conf.PRECISION_LEVELS]
    return [rawShape] + [MapistoShape(compressed_shape, conf.PRECISION_LEVELS[i]) for i, compressed_shape in enumerate(compressed_shapes) if compressed_shape is not None ]
    

def to_svg_path(polygon:Polygon):
    return ET.ElementTree(ET.fromstring(polygon.svg())).getroot().attrib['d'] 



def compress_land(land):
    assert isinstance(land, Land)
    return Land(land.land_id, get_compressed_shapes(land.representations[0]), land.bounding_box)
    
