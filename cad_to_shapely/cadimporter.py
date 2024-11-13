""" 

"""

import abc
import logging
from typing import List,Tuple


import shapely.geometry as sg
from shapely import ops
from shapely.geometry import Point, LineString


class CadImporter(abc.ABC):
    """
    Base abstract class. All cad importers should subclass this class.
    Imports CAD geometry into self.geometry
    """

    def __init__(self,filename : str):
        self.filename = filename
        self.units : str = None # unitless
        self.geometry : List[sg.base.BaseGeometry] = []
        self.polygons : List[sg.Polygon] = []
        self._already_zipped = False
    
    @abc.abstractmethod
    def process(self, **kwargs):
        """
        Converts CAD file formats geometry to our geometry.
        """
        pass

    def zip(self, zip_length: float = 0.000001):
        """
        Zip tries to reconcile not-quite-matching LineString start and end points.
        Point < zip_length apart will be equated.
        """

        zip = 0
        for i in range(len(self.geometry)):
            ls1 = self.geometry[i]
            fp_1 = Point(ls1.coords[0]) #startpoint
            lp_1 = Point(ls1.coords[-1]) #endpoint

            for j in range(i+1,len(self.geometry)):
                ls2 = self.geometry[j]
                fp_2 = Point(ls2.coords[0])
                lp_2 = Point(ls2.coords[-1])
                if fp_1.distance(fp_2) < zip_length and fp_1.distance(fp_2) != 0:
                    self.geometry[j] = LineString([ls1.coords[0]]+ls2.coords[1:])
                    zip += 1
                if fp_1.distance(lp_2) < zip_length and fp_1.distance(lp_2) != 0:
                    self.geometry[j]  = LineString(ls2.coords[:-1]+[ls1.coords[0]])
                    zip += 1
                if lp_1.distance(fp_2) < zip_length and lp_1.distance(fp_2) !=0:
                    self.geometry[j] = LineString([ls1.coords[-1]]+ls2.coords[1:])
                    zip += 1
                if lp_1.distance(lp_2) < zip_length and lp_1.distance(lp_2)!=0:
                    self.geometry[j] = LineString(ls2.coords[:-1]+[ls1.coords[-1]])
                    zip += 1 
        self._already_zipped = True
        logging.info(f"Zipped {zip} points")


    def polygonize(self, simplify = True, force_zip = False, zip_length = 0.000001, retry_with_zip = True):
        """
        Try and form polygons (closed shapes) from imported geometry
        """
    
        if not self.geometry:
            raise CadImporterError('Cannot run polygonize() since no geometry yet. Have you run process()?')

        if not force_zip:
            result, dangles, cuts, invalids = ops.polygonize_full(self.geometry)
            self.polygons = list(result.geoms)

        if force_zip or (not self.polygons and not self._already_zipped and retry_with_zip):
            self.zip(zip_length)
            
            result, dangles, cuts, invalids = ops.polygonize_full(self.geometry)
            self.polygons = list(result.geoms)

        if self.polygons:
            if simplify:
                for i,p in enumerate(self.polygons):
                    self.polygons[i] = self.polygons[i].simplify(0)
        else:
            logging.error("Unable to from any closed polygons.")    

        return result, dangles, cuts, invalids


    def cleanup(self, simplify = True, zip_length = 0.000001, retry_with_zip = True) -> str:    
        logging.info("cleanup is depreciated BTW. Use the polygonize function instead")
        self.polygonize(simplify,zip_length,retry_with_zip)
        return 'done'


    def bounds(self) -> Tuple[float]:
        """
        Returns, as (xmin,ymin,xmax,ymax) tuple, the bounding box which envelopes
        this importer's geometry
        """
        for g in self.geometry:
            b = g.bounds
            pass

class CadImporterError(Exception):
    pass

