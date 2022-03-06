import logging
import os
import math
from matplotlib.patches import Polygon

import numpy as np  

from geomdl import NURBS, BSpline, utilities
import ezdxf
from ezdxf.addons import Importer
import ezdxf.entities as entities
import shapely.geometry as sg

from cadimporter import CadImporter
import geometry
import matplotlib.pyplot as plt
import utils

class DxfImporter(CadImporter):

    def __init__(self,filename : str):
        super().__init__(filename)

    def _get_attribs(self, e : entities.DXFEntity):
        """

        """
        attribs = geometry._GeometryAttribs()
        attribs['layer'] = e.dxf.layer
        
        return attribs

    def _process_2d_polyline(self,polyline : entities.Polyline, degrees_per_segment : float = 1):
        xy = []

        for i,v1 in enumerate(polyline.vertices):
            xy.append([v1.dxf.location.x,v1.dxf.location.y])
            if v1.dxf.bulge and v1.dxf.bulge!=0:
                if i+1 == len(polyline.vertices):
                    if polyline.is_closed:
                        v2 = polyline.vertices[0]
                    else:
                        break
                else:
                     v2 = polyline.vertices[i+1]

                p1 = [v1.dxf.location.x,v1.dxf.location.y] 
                p2 = [v2.dxf.location.x,v2.dxf.location.y] 

                pts = utils.arc_points_from_bulge(p1,p2,v1.dxf.bulge,degrees_per_segment)
                pts = pts[1:-1]

                xy.extend(pts)

  #      for i, location in enumerate(polyline.points()): 
  #          xy.append([location.x, location.y])
        
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
        l = sg.LineString([
            (line.dxf.start.x,line.dxf.start.y),
            (line.dxf.end.x,line.dxf.end.y)
        ])

        if l.length > 0:
            self.geometry.append(l) 

    def _process_arc(self, arc: entities.Arc, degrees_per_segment : float = 1):
        """
        shapely does not do arcs, so we make it into an n-lined polyline.
        modified from here: https://stackoverflow.com/questions/30762329/how-to-create-polygons-with-arcs-in-shapely-or-a-better-library
        """
        start_angle = math.radians(arc.dxf.start_angle)
        end_angle = math.radians(arc.dxf.end_angle)
        if start_angle>end_angle:
            end_angle += 2 * math.pi

        pts =  utils.arc_points(
            start_angle,
            end_angle,
            arc.dxf.radius,
            [arc.dxf.center.x,arc.dxf.center.y],
            degrees_per_segment
        )

        arc = sg.LineString(pts)

        self.geometry.append(arc)


    def process(self, spline_delta = 0.1):
        """
        Args:
            spline_delta (float, optional): _description_. Defaults to 0.1

        Returns:
            str: report on geometry processed
        """

        sdoc = ezdxf.readfile(self.filename)
    
        ents = sdoc.modelspace().query('CIRCLE LINE ARC POLYLINE ELLIPSE SPLINE SHAPE')
        n_splines = n_polylines = n_lines = n_arcs =n_not_implemented = 0
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
                n_arcs += 1
            else:
                logging.warning(f'Importing of DXF type {type(e)} is not implemented yet.')
                logging.warning('Raise issue at https://github.com/aegis1980/cad-to-shapely/issues')
                n_not_implemented +=1

        return f'Found {n_polylines} polylines, {n_splines} splines, {n_lines} lines, {n_arcs} arcs. Could not process {n_not_implemented} entities.'
 