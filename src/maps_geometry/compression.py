from shapely.geometry import Polygon
import xml.etree.ElementTree as ET
from math import floor, log10
import numpy as np
from svgpath2mpl import parse_path


SVG_WORLDMAP_WIDTH = 2269.4568
EARTH_WIDTH = 40075
def compress(path, kilometer_precision):
    point_precision = SVG_WORLDMAP_WIDTH/EARTH_WIDTH * kilometer_precision
    heavy = Polygon(parse_path(path).to_polygons()[0])
    light = remove_too_close_coord(heavy, point_precision)
    if light==None:
    # Happens when the polygon is smaller than the precision, returns None (e.g. precision=20km , path is an island 10km wide)
        return None
    if point_precision >= 1 :
        # If precision is bigger than 1 pt, only removes the comma (i.e. no difference between precision 1pt and 1O pt)
        return to_svg_path(Polygon(np.around(light.exterior.coords))).replace('.0', '')
    else :
        # if precision smaller than 1 pts, truncate all coords to n decimals (1 decimal if precision==0.1 , 2 decimals if precision==0.09)
        nb_decimals = - floor(log10(point_precision))
        return to_svg_path(Polygon(np.around(light.exterior.coords, decimals=nb_decimals)))


def to_svg_path(polygon:Polygon):
    return ET.ElementTree(ET.fromstring(polygon.svg())).getroot().attrib['d'] 

def remove_too_close_coord(polygon, min_distance):
    coords = polygon.exterior.coords
    distance = lambda a, b : np.linalg.norm(np.subtract(a, b))
    res = [coords[0]]
    i=0
    while i < len(coords):
        gap = 1
        try :
            while distance(coords[i], coords[i+gap]) < min_distance:
                gap +=1
            res.append(coords[i+gap])
            
        except IndexError:
            pass
        i+=gap
    try :
        return Polygon(res)
    except ValueError:
        # When there are less than 3 points in res no polygon can be returned
        return None
