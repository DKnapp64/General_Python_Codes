import shapefile as shp
import csv

out_file = 'reef42_pairs.shp'

#Set up blank lists for data
id,x1,y1,x2,y2=[],[],[],[],[]

#read data from csv file and store in lists
with open('dimac_test_gray_reef42_temp2_Rb_test_gray_reef42_temp2_manual.pts', 'rb') as csvfile:
    r = csv.reader(csvfile, delimiter=',')
    for i,row in enumerate(r):
        x1.append(float(row[0]))
        y1.append(float(row[1]))
        x2.append(float(row[2]))
        y2.append(float(row[3]))
        id.append(i)

#Set up shapefile writer and create empty fields
w = shp.Writer(shp.POLYLINE)
w.autoBalance = 1 #ensures gemoetry and attributes match
w.field('ID','I',5)

#loop through the data and write the shapefile
for j,k in enumerate(x1):
    w.line(parts=[[[k,y1[j]],[x2[j],y2[j]]]]) #write the geometry
    w.record(id[j]) #write the attributes

#Save shapefile
w.save(out_file)

