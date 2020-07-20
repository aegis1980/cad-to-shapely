from typing import Union
import shapely.geometry as sg


class _GeometryAttribs(dict):
    pass


def patch_geometry_with_attribs(geometry : Union[sg.base.BaseGeometry, sg.base.BaseMultipartGeometry], attribs :_GeometryAttribs):
    """
    Add _attribs property to Shapely base geometry object, for meta data like layers, colour etc.
    """
    setattr(geometry, '_attribs', attribs)


