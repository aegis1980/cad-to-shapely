import os
import logging

import matplotlib.pyplot as plt

import dxf 
import utils 

def import_dxf_example1(filename : str, force_zip = False):
    """
    for debugging. just plots geometry with no polygon-making
    """
    dxf_filepath = os.path.join(os.getcwd(),'example_files',filename)
    my_dxf = dxf.DxfImporter(dxf_filepath)
    my_dxf.process(spline_delta = 0.1) 
    for g in my_dxf.geometry:
        x,y = g.xy
        plt.plot(x,y)
    plt.show()
    

def import_dxf_example(filename : str, force_zip = False):
    dxf_filepath = os.path.join(os.getcwd(),'example_files',filename)
    my_dxf = dxf.DxfImporter(dxf_filepath)
    my_dxf.process(spline_delta = 0.1)   
    my_dxf.polygonize(
        force_zip = force_zip
    )
    
    polygons = my_dxf.polygons
    print (f"Found {len(polygons)} polygons")

    for p in polygons:
        if p.interiors:
            print("interior")
        x,y = p.exterior.xy
        plt.plot(x,y)

    new = utils.find_holes(polygons)

    x,y = new.exterior.xy
    plt.plot(x,y)
    for hole in new.interiors:
        x,y = hole.xy
        plt.plot(x,y)

 
    for i in range(100):
        p=  utils.point_in_polygon(new)
        x,y = p.xy
        plt.plot(x, y, marker='o', markersize=3, color="red")
    plt.show()
    



if __name__ == "__main__":
    #logging.basicConfig(level = logging.DEBUG)
    #filename = "section_holes_complex.dxf"
    #filename = "simplelines_from_solidworks.dxf"
    filename = "200ub22_R12dxf_linesandarcs.dxf"
    
    #straight from http://www.steelweb.info/200x100x6.htm
    #filename = "200x100x6.dxf"

    filename = "test1.dxf"
   # filename = "test2.dxf"
    #filename = "test3.dxf"
    import_dxf_example(filename)