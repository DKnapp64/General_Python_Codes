import shapefile as shp
import csv

csvfile = 'Database_15082016_from_Becca.csv'
outfile = 'database_15082016_from_becca.shp'

#Set up blank lists for data
photoname,x,y,coralbrown,algalturf,corallinealgae,sand = [],[],[],[],[],[],[]

#read data from csv file and store in lists
## with open('/caofs/scratch/dave/dogs/den_random_points_20150723.csv', 'rb') as csvfile:
with open(csvfile, 'rb') as csvfile:
    r = csv.reader(csvfile, delimiter=',')
    for i,row in enumerate(r):
        photoname.append(row[0])
        x.append(float(row[1]))
        y.append(float(row[2]))
        coralbrown.append(int(row[3]))
        algalturf.append(int(row[4]))
        corallinealgae.append(int(row[5]))
        sand.append(int(row[6]))

#Set up shapefile writer and create empty fields
w = shp.Writer(shp.POINT)
w.autoBalance = 1 #ensures geometry and attributes match
w.field('CORALBROWN','N',4)
w.field('ALGALTURF','N',4)
w.field('CORALINALG','N',4)
w.field('SAND','N',4)
w.field('PHOTONAME','C',20)

#loop through the data and write the shapefile
for j,k in enumerate(x):
    w.point(k, y[j]) #write the geometry
    w.record(coralbrown[j], algalturf[j], corallinealgae[j], sand[j], photoname[j]) #write the attributes

#Save shapefile
w.save(outfile)
