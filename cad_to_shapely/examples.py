import os
import matplotlib.pyplot as plt

import dxf 
import utils 


def import_dxf_example():
    dxf_filepath = os.path.join(os.getcwd(),'example_files','section_holes_complex.dxf')
    my_dxf = dxf.DxfImporter(dxf_filepath)
    my_dxf.process(spline_delta = 0.5)   
    my_dxf.cleanup()
    
    polygons = my_dxf.polygons
    for p in polygons:
        x,y = p.exterior.xy
 

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
    import_dxf_example()