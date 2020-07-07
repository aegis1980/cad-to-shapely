from typing import List
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


def find_holes(polygons : List[sg.Polygon]):
    """
    Returns a single polygon with holes, built from a list of (imported CAD) polygons
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