import shapefile as shp
import math

# Make a series of Grid cells covering Ecuador
w = shp.Writer(shp.POLYGON)
startpt = (650000.0, 10100000.0)

minx,maxx,miny,maxy = 650000.00, 1150000.00, 9400000.00, 10100000.00
dx = 25000
dy = 25000

nx = int(math.ceil(abs(maxx - minx)/dx))
ny = int(math.ceil(abs(maxy - miny)/dy))

w = shp.Writer(shp.POLYGON)
w.autoBalance = 1
w.field("NAME", 'C', 3, 0)
w.field("ID")
id=0
name=''
alpha = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T']

for i in range(ny):
    for j in range(nx):
        id += 1
        name = alpha[j] + ('%02i' % (i+1))
        vertices = []
        parts = []
        vertices.append([min(minx+dx*j,maxx),max(maxy-dy*i,miny)])
        vertices.append([min(minx+dx*(j+1),maxx),max(maxy-dy*i,miny)])
        vertices.append([min(minx+dx*(j+1),maxx),max(maxy-dy*(i+1),miny)])
        vertices.append([min(minx+dx*j,maxx),max(maxy-dy*(i+1),miny)])
        parts.append(vertices)
        w.poly(parts)
        w.record(name, id)

w.save('Ecuador_25km_grid')
