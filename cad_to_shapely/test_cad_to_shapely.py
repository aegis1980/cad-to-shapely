import os
import matplotlib.pyplot as plt

import dxf
import utils


def test_complex_holes_section():
    dxf_filepath = os.path.join(os.getcwd(),'example_files','section_holes_complex.dxf')
    my_dxf = dxf.DxfImporter(dxf_filepath)
    my_dxf.process(spline_delta = 0.5)
    my_dxf.cleanup()

    polygons = my_dxf.polygons
    assert len(polygons) == 3