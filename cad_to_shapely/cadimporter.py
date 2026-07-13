""" 

"""

import abc
import logging
from typing import List,Tuple


import shapely.geometry as sg
from shapely import ops
from shapely.geometry import Point, LineString

# Adaptive zip tolerance, as a fraction of the geometry's larger bounding-box
# dimension. Real-world CAD linework routinely has micron-scale endpoint gaps
# which a fixed tolerance in drawing units cannot absorb across mm/m/inch files.
RELATIVE_ZIP_LENGTH = 0.00001
# Fallback zip tolerance when the geometry extents are degenerate (or empty).
ABSOLUTE_ZIP_LENGTH = 0.000001


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

    def suggested_zip_length(self) -> float:
        """
        Snapping tolerance scaled to the extents of the imported geometry
        (RELATIVE_ZIP_LENGTH of the larger bounding-box dimension), so it works
        for drawings in mm, metres or inches alike.
        """
        b = self.bounds()
        if b is None:
            return ABSOLUTE_ZIP_LENGTH
        extent = max(b[2] - b[0], b[3] - b[1])
        if extent <= 0:
            return ABSOLUTE_ZIP_LENGTH
        return extent * RELATIVE_ZIP_LENGTH

    def zip(self, zip_length: float = None):
        """
        Zip tries to reconcile not-quite-matching LineString start and end points.
        Point < zip_length apart will be equated.
        Defaults (zip_length=None) to the adaptive suggested_zip_length().
        """
        if zip_length is None:
            zip_length = self.suggested_zip_length()

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


    def polygonize(self, simplify = True, force_zip = False, zip_length = None, retry_with_zip = True):
        """
        Try and form polygons (closed shapes) from imported geometry.
        zip_length=None uses the adaptive suggested_zip_length() when zipping.
        """
    
        if not self.geometry:
            raise CadImporterError('Cannot run polygonize() since no geometry yet. Have you run process()?')

        incomplete = True
        if not force_zip:
            result, dangles, cuts, invalids = ops.polygonize_full(self.geometry)
            self.polygons = list(result.geoms)
            # leftover cuts or dangles mean some linework failed to form a ring,
            # e.g. the inner boundary of a hollow section with tiny gaps in it.
            incomplete = not self.polygons or len(cuts.geoms) > 0 or len(dangles.geoms) > 0

        if force_zip or (incomplete and not self._already_zipped and retry_with_zip):
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


    def cleanup(self, simplify = True, zip_length = None, retry_with_zip = True) -> str:
        logging.info("cleanup is depreciated BTW. Use the polygonize function instead")
        self.polygonize(simplify=simplify, zip_length=zip_length, retry_with_zip=retry_with_zip)
        return 'done'


    def bounds(self) -> Tuple[float]:
        """
        Returns, as (xmin,ymin,xmax,ymax) tuple, the bounding box which envelopes
        this importer's geometry. None if there is no geometry.
        """
        if not self.geometry:
            return None
        xmin, ymin = float('inf'), float('inf')
        xmax, ymax = float('-inf'), float('-inf')
        for g in self.geometry:
            b = g.bounds
            xmin, ymin = min(xmin, b[0]), min(ymin, b[1])
            xmax, ymax = max(xmax, b[2]), max(ymax, b[3])
        return (xmin, ymin, xmax, ymax)

class CadImporterError(Exception):
    pass

