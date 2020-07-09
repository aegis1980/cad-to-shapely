
import xml.etree.ElementTree as ET
import os
import gzip
import shutil
from typing import List,Dict

from shapely.geometry import LineString

from cadimporter import CadImporter


class _SvgPath():
    """
    Generic SVGpath. Geometry defined by attribute 'd'
    https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/d

    MoveTo: M, m
    LineTo: L, l, H, h, V, v
    Cubic Bézier Curve: C, c, S, s
    Quadratic Bézier Curve: Q, q, T, t
    Elliptical Arc Curve: A, a
    ClosePath: Z, z

    Note: 
    Commands are case-sensitive. An upper-case command specifies absolute coordinates,
    while a lower-case command specifies coordinates relative to the current position
    """

    def __init__(self):
        self.d = None
        self.stroke = '#000000'
        self.fill = None

    def is_valid(self):
        return self.d is not None

    def to_dash_dict(self):
        return dict (
            type = 'path',
            path = self.d,
            line_color = 'Black', 
            fillcolor = self.fill
        )

    @classmethod
    def from_linestring(cls, ls : LineString):
        """
        Converts shapely.geometry.LineString to SVG path. 
        Shapely can produce SVG output using linestring._repr_svg_() but it
        produces an SVG XML using polygon, not (more generic and plotly-friendly) path
        """
        c = cls()
        c.d = ''
        for i,p in enumerate(ls.coords):
            if i==0:
                c.d +='M {:f} {:f} '.format(p[0],p[1]) 
            else:
                c.d +='L {:f} {:f} '.format(p[0],p[1]) 
        if ls.is_closed:
            c.d += 'Z'
            c.fill = '#000000'

        return c


class SvgImporter(CadImporter):

    def __init__(self, filename :str):
        super().__init__(filename)
        self.paths = []


    def process(self, origin = None, flip_x = False, flip_y = False) -> List[Dict]:
        """
        returns plotly shapes as array of dicts
        use '

        """

        # unzip .svgz file into .svg
        if isinstance(self.filename, str) and os.path.splitext(self.filename[1].lower() == ".svgz"):
            with gzip.open(self.filename, 'rb') as f_in, open(self.filename[:-1], 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            self.filepath = self.filepath[:-1]
    
        tree = ET.parse(self.filepath)
        root = tree.getroot()
        for child in root:
            if child.tag.endswith('path'):
                path = _SvgPath()
                if 'd' in child.attrib:
                    #Note: 
                    # Commands are case-sensitive. An upper-case command specifies absolute coordinates, 
                    # while a lower-case command specifies coordinates relative to the current position
                    path.d = child.attrib['d']
                if 'stroke' in child.attrib:
                    path.stroke = child.attrib['stroke']           
                if 'fill' in child.attrib:
                    path.fill =  child.attrib['fill']
                if 'stroke-width' in child.attrib:
                    path.stroke_width = child.attrib['stroke-width']
                
                if path.is_valid():
                    self.paths.append(path)


        shapes = []
        for path in self.paths:
            shapes.append(path.to_dash_dict())

        return shapes




 
            

