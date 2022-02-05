from typing import List,Tuple, Union
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
    for p in polygons:
        if p.interiors:
            return p

    #sort by areas, largest first.
    polygons.sort(key=lambda x: x.area, reverse=True)
    print([p.area for p in polygons])
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



def arc_points(start_angle : float, end_angle : float, radius : float, center : List[float], degrees_per_segment : float) -> list:
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

    # mid point between p1 & p2
    m = [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2]

    d = distance(p1,p2)
    radius = d*((b**2)+1)/ (4*b)
    
    # find centre
    # https://stackoverflow.com/a/36211304/772333
    k = math.sqrt((radius**2)-(d/2)**2)
    base_x = k*(p1[1]-p2[1])/d
    base_y = k*(p2[0]-p1[0])/d

    if b<0:
        center = [m[0]+ base_x, m[1] + base_y]
    else:
        center = [m[0] + base_x, m[1] + base_y]

    logging.debug(f'radius {radius:.1f} : distance {d:.1f} : centre {center[0]:.1f},{center[0]:.1f}')


    start_angle = math.atan2(p1[1]-center[1], p1[0]-center[0])
    end_angle = math.atan2(p2[1]-center[1], p2[0]-center[0])

    if start_angle>end_angle:
        end_angle += 2 * math.pi

    return arc_points(start_angle,end_angle,radius,center,degrees_per_segment)