import shapefile as shp
import csv

csvfile = 'sabah_kuamut.csv'
outfile = 'sabah_kuamut.shp'

#Set up blank lists for data
plotid,x,y,elev = [],[],[],[]

#read data from csv file and store in lists
## with open('/caofs/scratch/dave/dogs/den_random_points_20150723.csv', 'rb') as csvfile:
with open(csvfile, 'rb') as csvfile:
    r = csv.reader(csvfile, delimiter=',')
    for i,row in enumerate(r):
        plotid.append(row[0])
        x.append(float(row[2]))
        y.append(float(row[1]))
        elev.append(int(row[3]))

#Set up shapefile writer and create empty fields
w = shp.Writer(shp.POINT)
w.autoBalance = 1 #ensures geometry and attributes match
w.field('PLOTID','C',16)
w.field('ELEV','N',4)

#loop through the data and write the shapefile
for j,k in enumerate(x):
    w.point(k, y[j]) #write the geometry
    w.record(plotid[j], elev[j]) #write the attributes

#Save shapefile
w.save(outfile)
