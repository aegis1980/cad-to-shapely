import abc
from typing import List,Tuple

import shapely.geometry as sg
from shapely import ops

class CadImporter(abc.ABC):
    """
    Base abstract class. All cad importers should subclass this class.
    Imports CAD geometry into self.geometry
    """

    def __init__(self,filename : str):
        self.filename = filename
        self.geometry : List[sg.base.BaseGeometry] = []
        self.polygons : List[sg.Polygon] = []
    
    @abc.abstractmethod
    def process(self, **kwargs):
        """
        Converts CAD file formats geometry to our geometry.
        """
        pass

    def cleanup(self) -> str:
        if not self.geometry:
            return 'no cleanup since no geometry. have you run process yet?'


        multiline = sg.MultiLineString(self.geometry)
        #merge = ops.linemerge(multiline)

        result, dangles, cuts, invalids = ops.polygonize_full(self.geometry)
        self.polygons = list(result)
        return 'done'


    def bounds(self) -> Tuple[float]:
        """
        Returns, as (xmin,ymin,xmax,ymax) tuple, the bounding box which envelopes
        this importer's geometry
        """
        for g in self.geometry:
            b = g.bounds
            pass


