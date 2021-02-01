import shapefile as shp
import csv

csvfile = 'KaneoheGPSPoints06-09Nov2017.csv'
outfile = 'KaneoheGPSPoints06-09Nov2017.shp'

#Set up blank lists for data
Site,Species,Tag,Lat,Long = [],[],[],[],[]

#read data from csv file and store in lists
## with open('/caofs/scratch/dave/dogs/den_random_points_20150723.csv', 'rb') as csvfile:
with open(csvfile, 'rb') as csvfile:
    r = csv.reader(csvfile, delimiter=',')
    for i,row in enumerate(r):
        Site.append(row[0])
        Species.append(row[1])
        Tag.append(row[2])
        Lat.append(float(row[3]))
        Long.append(float(row[4]))

#Set up shapefile writer and create empty fields
w = shp.Writer(shp.POINT)
w.autoBalance = 1 #ensures geometry and attributes match
w.field('Site','C',4)
w.field('Species','C',20)
w.field('Tag','C',20)

#loop through the data and write the shapefile
for j,k in enumerate(Long):
    w.point(k, Lat[j]) #write the geometry
    w.record(Site[j], Species[j], Tag[j]) #write the attributes

#Save shapefile
w.save(outfile)
