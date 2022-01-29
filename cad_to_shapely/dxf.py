import os
import math

import numpy as np  

from geomdl import NURBS, BSpline, utilities
import ezdxf
from ezdxf.addons import Importer
import ezdxf.entities as entities
import shapely.geometry as sg

from cadimporter import CadImporter
import geometry


class DxfImporter(CadImporter):

    def __init__(self,filename : str):
        super().__init__(filename)

    def _get_attribs(self, e : entities.DXFEntity):
        """

        """
        attribs = geometry._GeometryAttribs()
        attribs['layer'] = e.dxf.layer
        
        return attribs

    def _process_2d_polyline(self,polyline):
        xy = []
        polyline
        for i, location in enumerate(polyline.points()): 
            xy.append([location.x, location.y])
        
        if polyline.is_closed:    
            pl = sg.LinearRing(xy)
        else:
            pl = sg.LineString(xy)
        self.geometry.append(pl) 
        

    def _process_2d_spline(self,spline : entities.Spline, delta = 0.1):
        """
        Uses geomdl module to create intermediate b-spline from dxf spline.
        This is then sampled as a linestring since shapely does not support splines. 
        """

        curve = NURBS.Curve()
        curve.degree = spline.dxf.degree
        curve.ctrlpts = spline.control_points
        
        curve.weights = [1] * spline.control_point_count()#spline.weights
        #curve.weights = spline.weights + [1] * np.array(spline.control_point_count()- len(spline.weights))
        curve.knotvector = spline.knots
 
        curve.delta = delta # TODO sampling - this could get out of hand depending on model dims and scale

        #TODO conditional delta: min length, n and check for straight lines

        xyz = np.array(curve.evalpts)

        #discard z data 
        xy = list([x[:-1] for x in xyz])

        pl = sg.LineString(xy)
        # geometry.patch_geometry_with_attribs(pl,self._get_attribs(spline))

        self.geometry.append(pl)
  
    def _process_line(self, line : entities.Line):
        l = sg.LineString([line.start(), line.end()])
        if l.length > 0:
            self.geometry.append(l) 

    def process_arc(self, arc: entities.Arc, segments_per_degree : float = 2):
        """
        shapely does not do arcs, so we make it into an n-lined polyline.
        modified from here: https://stackoverflow.com/questions/30762329/how-to-create-polygons-with-arcs-in-shapely-or-a-better-library
        """
        start_angle = math.radians(arc.dxf.start_angle)
        end_angle = math.radians(arc.dxf.start_angle)


        # The coordinates of the arc
        theta = np.radians(np.linspace(start_angle, end_angle, numsegments))
        x = cx + r * np.cos(theta)
        y = cy + r * np.sin(theta)

        arc = sg.LineString(np.column_stack([x, y]))


    def process(self, spline_delta = 0.1, fillcolor = '#ff0000'):
        """
        implement superclass abstract method
        uses ezdxf to read dxf file and populate geometry
        """
        sdoc = ezdxf.readfile(self.filename)
    
        ents = sdoc.modelspace().query('CIRCLE LINE ARC POLYLINE ELLIPSE SPLINE SHAPE')
        n_splines = n_polylines = n_lines = 0
        for e in ents:
            if isinstance(e, entities.Spline) and e.dxf.flags >= ezdxf.lldxf.const.PLANAR_SPLINE:
                self._process_2d_spline(e, delta= spline_delta)
                n_splines +=1
            elif isinstance(e, entities.Polyline):
                if e.get_mode() == 'AcDb2dPolyline':
                    self._process_2d_polyline(e)
                    n_polylines += 1
                else:
                    pass
            elif isinstance(e, entities.Line):
                self._process_line(e)
                n_lines += 1

            elif isinstance(e, entities.Arc):
                self._process_arc(e)

        return f'Found {n_polylines} polylines, {n_splines} splines, {n_lines} lines'
 