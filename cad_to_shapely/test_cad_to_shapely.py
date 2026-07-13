import os
import dxf, utils

def area_check(filename,area,tol =0.1):
    dxf_filepath = os.path.join(os.getcwd(),'example_files',filename)
    my_dxf = dxf.DxfImporter(dxf_filepath)
    my_dxf.process()
    my_dxf.polygonize()

    section = utils.find_holes(my_dxf.polygons)
    return abs(section.area - area)<tol


def test_complex_holes_section():
    dxf_filepath = os.path.join(os.getcwd(),'example_files','section_holes_complex.dxf')
    my_dxf = dxf.DxfImporter(dxf_filepath)
    my_dxf.process(spline_delta = 0.5)
    my_dxf.polygonize()

    polygon_with_holes = utils.find_holes(my_dxf.polygons)
    polygon_with_holes.interiors
    assert len(polygon_with_holes.interiors) == 2 


def test_simplelines_from_solidworks():
    dxf_filepath = os.path.join(os.getcwd(),'example_files','simplelines_from_solidworks.dxf')
    my_dxf = dxf.DxfImporter(dxf_filepath)
    my_dxf.process()
    my_dxf.polygonize()

    polygons = my_dxf.polygons
    assert len(polygons) == 1


def test_dxf_r14_lines_and_arcs():
    dxf_filepath = os.path.join(os.getcwd(),'example_files','200ub22_R12dxf_linesandarcs.dxf')
    my_dxf = dxf.DxfImporter(dxf_filepath)
    my_dxf.process()
    my_dxf.polygonize()

    polygons = my_dxf.polygons
    assert len(polygons) == 1


def test_hollow_section_from_steelweb_dot_info():
    assert area_check('200x100x6.dxf',3373.593)


def test_aluminium_extrusion1():
    area = 884.2 # mm2 calculated in Rhino 3d
    assert area_check('test1.dxf',area)



def test_aluminium_extrusion2():
    area = 1266.0661  # mm2 calculated in Rhino 3d
    assert area_check('test2.dxf',area)


def test_aluminium_extrusion3():
    area = 681.9 # mm2 calculated in Rhino 3d
    assert area_check('test3.dxf',area)


def test_tophat_lwpolyline():
    area = 789.552272
    assert area_check('tophat_autocadlite.dxf', area)

def test_circles_and_polygons():
    dxf_filepath = os.path.join(os.getcwd(),'example_files','tophat_circles_autocadlite.dxf')
    my_dxf = dxf.DxfImporter(dxf_filepath)
    my_dxf.process()
    my_dxf.polygonize()

    polygons = my_dxf.polygons
    assert len(polygons) == 3


def test_arcs_with_negative_extrusion():
    """
    Mirrored entities are written with an OCS extrusion of (0,0,-1); their raw
    coordinates must be transformed to WCS or the section outline never closes.
    """
    dxf_filepath = os.path.join(os.getcwd(),'example_files','hollow_section_mirrored_arcs.dxf')
    my_dxf = dxf.DxfImporter(dxf_filepath)
    my_dxf.process()
    my_dxf.polygonize()

    sections = utils.filter_polygons(my_dxf.polygons)
    assert len(sections) == 1
    assert len(sections[0].interiors) == 1
    assert abs(sections[0].area - 1707.7) < 0.5


def test_micro_gaps_zipped():
    """
    Same hollow section, drawn with two ~0.85 micron gaps in the inner ring.
    The adaptive zip tolerance must close them so the hole is not lost.
    """
    dxf_filepath = os.path.join(os.getcwd(),'example_files','hollow_section_micro_gaps.dxf')
    my_dxf = dxf.DxfImporter(dxf_filepath)
    my_dxf.process()
    my_dxf.polygonize()

    sections = utils.filter_polygons(my_dxf.polygons)
    assert len(sections) == 1
    assert len(sections[0].interiors) == 1
    assert abs(sections[0].area - 1707.7) < 0.5