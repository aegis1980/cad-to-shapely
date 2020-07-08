from typing import List,Tuple
import random

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