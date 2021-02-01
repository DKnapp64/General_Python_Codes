import shapefile as shp
import csv

## out_file = 'roi_seki_combined.shp'
out_file = 'spratly_atoll_points.shp'

#Set up blank lists for data
id,x1,y1=[],[],[]

#read data from csv file and store in lists
with open('/home/dknapp/python_stuff/atoll_points.csv', 'rb') as csvfile:
    r = csv.reader(csvfile, delimiter=',')
    for i,row in enumerate(r):
        x1.append(float(row[2]))
        y1.append(float(row[1]))
        id.append(row[0])

#Set up shapefile writer and create empty fields
w = shp.Writer(shp.POINT)
w.autoBalance = 1 #ensures gemoetry and attributes match
w.field('ID','I',5)

#loop through the data and write the shapefile
for j,k in enumerate(x1):
    w.point(k,y1[j]) #write the geometry
    w.record(id[j]) #write the attributes

#Save shapefile
w.save(out_file)

