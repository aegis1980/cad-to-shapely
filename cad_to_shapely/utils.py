
from typing import List
import random
import math
import logging

import numpy as np
import shapely.geometry as sg




def point_in_polygon(polygon :sg.Polygon, limit = 1000):
    """
    Find a point in a polygon
    """
    i = 0 
    minx, miny, maxx, maxy = polygon.bounds
    while i < limit:
        i +=1
        pnt = sg.Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if polygon.contains(pnt):
            return pnt
    return None


def find_holes(polygons : List[sg.Polygon]) -> sg.Polygon:
    """
    Construct single polygon from imported CAD goemetry. 
    Assumes there is only one parent shape (the one with the largest gross area.)

    Access external perimeter with *polygon.exterior*
    Access holes perimeter(s, if there are any) with *polygon.interiors*

    Returns:
        Shapely Polygon with holes 
    """
    import warnings
    warnings.warn("find_holes is deprecated; use filter_polygons", DeprecationWarning)
    
    for p in polygons:
        if p.interiors:
            return p

    #sort by areas, largest first.
    polygons.sort(key=lambda x: x.area, reverse=True)
    parent = polygons.pop(0)

    keepers = []
    for p in polygons:
        if p.within(parent):
            valid = True
            for q in polygons:
                if (p.intersects(q) or p.within(q)) and p is not q:
                    valid = False
           
            if valid: keepers.append(p)


    new = sg.Polygon(parent,holes=keepers)
    return new


def filter_polygons(polygons : List[sg.Polygon], filter_flag:int = 3) -> List[sg.Polygon]:
    """
    Remove polygons that describe interior rings within a exterior rings so returned list only return
    'surfaces'' (polygons in shapely) that either have holes, not holes or both (default)

    Args:
        polygons (List[sg.Polygons]): list of raw polygons
        inc_flag (int): 1 = only surfaces with holes, 2 only surfaces without holes, 3 = both (default)

    Returns:
        Shapely Polygons both/withboth holes 
    """

    idx_hole_polygons = []    # polygons defining a hole. these get scrapped whatever
    idx_poly_with_holes = []
    idx_poly_no_holes = []

    for i,p in enumerate(polygons):
        if p.interiors:
            idx_poly_with_holes.append(i)
            for hole in p.interiors:
                for j,r in enumerate(polygons):
                    if i == j:
                        continue
                    if r.exterior.equals(hole):
                        idx_hole_polygons.append(j)
        else:
            idx_poly_no_holes.append(i)
                        
    if filter_flag == 1: # keep the holy ones, get rid of ones without hoels
        idx_poly_to_remove = idx_hole_polygons + idx_poly_no_holes
    elif filter_flag == 2: #keep the non-holy ones.
        idx_poly_to_remove = idx_hole_polygons + idx_poly_with_holes
    else:
        idx_poly_to_remove = idx_hole_polygons

    #remove repeats so do screw up indexes in filtering step.
    idx_poly_to_remove = sorted(list(set(idx_poly_to_remove)))

                        
    return [ele for idx, ele in enumerate(polygons) if idx not in idx_poly_to_remove] 




def facets(polygon: sg.Polygon, inc_holes =True):
    n = len(polygon.exterior.xy[0])
    f = []
    for i in range(n-1):
        f.append([i, i+1])
    f.append([n-1,0])

    if inc_holes:
        for hole in polygon.interiors:
            lastn = len(f)        
            n = len(hole.xy[0])
            g = []
            for i in range(lastn, lastn+n-1):
                g.append([i, i+1])
            g.append([lastn+n-1,lastn])
            f.extend(g)
    
    return f


def distance(p1 : List[float],p2 : List[float]) -> float:
    return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)



def arc_points(
    start_angle : float, 
    end_angle : float, 
    radius : float, 
    center : List[float], 
    degrees_per_segment : float
    ) -> list:
    """
    Coordinates of an arcs (for approximation as a polyline)

    Args:
        start_angle (float): arc start point relative to centre, in radians
        end_angle (float): arc end point relative to centre, in radians
        radius (float): [description]
        center (List[float]): arc centre as [x,y]
        degrees_per_segment (float): [description]

    Returns:
        list: 2D list of points as [x,y]
    """
    

    n = abs(int((end_angle-start_angle)/ math.radians(degrees_per_segment))) #number of segments
    theta = np.linspace(start_angle, end_angle, n)

    x = center[0] + radius * np.cos(theta)
    y = center[1] + radius * np.sin(theta)

    return np.column_stack([x, y])



def arc_points_from_bulge(p1 : List[float], p2 : List[float], b : float, degrees_per_segment : float):
    """
    http://darrenirvine.blogspot.com/2015/08/polylines-radius-bulge-turnaround.html

    Args:
        p1 (List[float]): [description]
        p2 (List[float]): [description]
        b (float): bulge of the arc
        degrees_per_segment (float): [description]

    Returns:
        [type]: point on arc
    """

    theta = 4 *math.atan(b)
    u = distance(p1,p2)

    r = u*((b**2)+1)/ (4*b)

    try:
        a = math.sqrt(r**2-(u*u/4))
    except ValueError:
        a = 0
    
    dx = (p2[0]-p1[0])/u
    dy = (p2[1]-p1[1])/u

    A = np.array(p1)
    B = np.array(p2)
    # normal direction
    N = np.array([dy,-dx])


    # if bulge is negative arc is clockwise
    # otherwise counter-clockwise
    s = b/abs(b) #sigma = signum(b)
    
    #centre, as a np.array 2d point

    if abs(theta) <= math.pi:
        C = ((A+B)/2) - s*a*N
    else:
        C = ((A+B)/2) + s*a*N

    logging.debug(f'radius {r:.1f} : distance {u:.1f} : centre {C[0]:.1f},{C[1]:.1f}')


    start_angle = math.atan2(p1[1]-C[1], p1[0]-C[0])
    if b<0:
        start_angle += math.pi
    
    
    end_angle = start_angle + theta

    return arc_points(start_angle,end_angle,r,C,degrees_per_segment)