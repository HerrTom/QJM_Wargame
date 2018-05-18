import os
import xlrd
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d

# set the working directory to the script location
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# function to output kml file
def gen_kml_polygon(name,desc,verts,):
    """
    Outputs a string for a KML polygon
    """
    
    polygon = """    <Placemark>
		<name>{}</name>
		<description>{}</description>
		<styleUrl>#m_ylw-pushpin</styleUrl>
		<Polygon>
			<tessellate>1</tessellate>
			<outerBoundaryIs>
				<LinearRing>
					<coordinates>
						{}
					</coordinates>
				</LinearRing>
			</outerBoundaryIs>
		</Polygon>
        </Placemark>
    """.format(name,desc,verts)
    
    return polygon

def write_kml(filename,polygons):
    head = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
    <Document>
        <name>{}</name>
        """.format(filename)
    main = ""
    for poly in polygons:
        main += poly
    tail = """  </Document>
</kml>"""
    output = head+main+tail
    with open(filename,'w+') as f:
        f.write(output)

def coords_to_kml_points(coords):
    kml = ""
    for coord in coords:
        kml += "{},{},0 ".format(coord[1],coord[0])
    # last entry is the first entry
    kml += "{},{},0 ".format(coords[0][1],coords[0][0])
    return kml

def read_shapes(sheet):
    # reads shapes from the sheet and returns an array of coordinates
    lat = sheet.col_values(0)
    del lat[0]
    lon = sheet.col_values(1)
    del lon[0]
    ids = sheet.col_values(2)
    del ids[0]
    unique_ids = set(ids)
    coords = list()
    for id in unique_ids:
        coord_set = list()
        for idx, n in enumerate(ids):
            if n == id:
                coord_set.append((lat[idx],lon[idx]))
        coords.append(coord_set)
    return coords
        
    
    
book = xlrd.open_workbook("unit_locations.xlsx")
unitsheet   = book.sheet_by_index(0)

unit_names  = unitsheet.col_values(0)
unit_sides  = unitsheet.col_values(1)
unit_lat    = unitsheet.col_values(2)
unit_lon    = unitsheet.col_values(3)

bound_sheet = book.sheet_by_index(1)
# bound_lat   = bound_sheet.col_values(0)
# bound_lon   = bound_sheet.col_values(1)
coords = read_shapes(bound_sheet)

# delete the headers
del unit_names[0]
del unit_sides[0]
del unit_lat[0]
del unit_lon[0]

unit_coords = list(zip(unit_lon,unit_lat))
# bound_coords = list(zip(bound_lon,bound_lat))

vor = Voronoi(unit_coords)

# plt.plot(unit_lat,unit_lon,'bo')

# try writing a kml file from unit positions
poly = list()
for n in range(len(coords)):
    verts = coords_to_kml_points(coords[n])
    poly.append(gen_kml_polygon("Test {}".format(n),"Test description",verts,))
write_kml("advance_test.kml",poly)

voronoi_plot_2d(vor)
plt.show()
