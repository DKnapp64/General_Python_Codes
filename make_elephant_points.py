import shapefile as shp
import csv

csvfile = 'HiP_Elephants_Viewsheds_100m.csv'
outfile = 'HiP_Elephants_Viewsheds_100m.shp'

#Set up blank lists for data
pointname,x,y = [],[],[]

#read data from csv file and store in lists
## with open('/caofs/scratch/dave/dogs/den_random_points_20150723.csv', 'rb') as csvfile:
with open(csvfile, 'rb') as csvfile:
    r = csv.reader(csvfile, delimiter=',')
    for i,row in enumerate(r):
        pointname.append(row[0])
        x.append(float(row[1]))
        y.append(float(row[2]))

#Set up shapefile writer and create empty fields
w = shp.Writer(shp.POINT)
w.autoBalance = 1 #ensures geometry and attributes match
w.field('POINTNAME','C',5)

#loop through the data and write the shapefile
for j,k in enumerate(x):
    w.point(k, y[j]) #write the geometry
    w.record(pointname[j]) #write the attributes

#Save shapefile
w.save(outfile)
