from shapely.geometry import Polygon
from svgpath2mpl import parse_path
import xml.etree.ElementTree as ET

def path_to_polygon(path):
    return Polygon(parse_path(path).to_polygons()[0])

def to_svg_path(polygon: Polygon):
    return ET.ElementTree(ET.fromstring(polygon.svg())).getroot().attrib['d']

