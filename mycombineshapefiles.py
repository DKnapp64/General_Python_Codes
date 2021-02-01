#!/usr/bin/env python3
import sys
import os
##import glob
import fnmatch
import subprocess

import ogr

def usage(name):
    sys.stdout.write("{} [-n|--dryrun] [-f|--format FMT] [-m|--name NAME] [-k|--kml NAME] [--kmllco* STR] [--ogropt* STR] ".format(name)+
                     "[--lco* STR] --[-o|--output NAME] [-d|--dir PATH PATTERN] [PATH PATH ...]\n")
    return

def names_match(file, nameslist):
    fileref = ogr.Open(file)
    if not fileref:
        raise RuntimeError("Could not open file with OGR")
    layerref = fileref.GetLayer(0)
    if not layerref:
        raise RuntimeError("Could not open layer 0 with OGR")
    defn = layerref.GetLayerDefn()
    if not defn:
        raise RuntimeError("Could not get feature definition for layer 0")
    layernames = [defn.GetFieldDefn(fi).GetName() for fi in range(defn.GetFieldCount())]
    if not nameslist:
        nameslist.extend(layernames)
        return True
    else:
        if len(nameslist) != len(layernames):
            return False
        if any([layernames[i] != nameslist[i] for i in range(len(nameslist))]):
            return False
    return True

def main():
    args = sys.argv
    name = os.path.basename(args.pop(0))
    shapelist = []
    kmlname = None
    outname = None
    namefield = None
    ogrformat = None
    ogropts = []
    lcopts = []
    kmlopts = []
    echoonly = False
    while args:
        arg = args.pop(0)
        if arg in ('-h','-help','--help'):
            usage(name)
            sys.exit(0)
        elif arg in ('-o','--output'):
            outname = args.pop(0)
        elif arg in ('-f','--format'):
            ogrformat = args.pop(0)
        elif arg in ('-k','--kml'):
            kmlname = args.pop(0)
        elif arg in ('-m','--name'):
            namefield = args.pop(0)
        elif arg in ('-d','--dir'):
            rootname = args.pop(0)
            filepattern = args.pop(0)
            dirshapes = []
            for root, dirnames, filenames in os.walk(rootname):
                for filename in fnmatch.filter(filenames, filepattern):
                    dirshapes.append(os.path.join(root, filename))
            shapelist.extend(sorted(dirshapes))
        elif arg in ('-n','--dryrun'):
            echoonly = True
        elif arg == "--kmllco":
            kmlopts.append(args.pop(0))
        elif arg == "--ogropt":
            ogropts.append(args.pop(0))
        elif arg == "--lco":
            lcopts.append(args.pop(0))
        elif arg[0] == '-':
            sys.stderr.write('{}: Cannot understand argument {}\n'.format(name,arg))
            sys.exit(99)
        else:
            shapelist.append(arg)
    ##Check for given outname
    if not outname:
        if not ogrformat:
            outname = "combined_shapes.shp"
        else:
            sys.stderr.write('{}: If format is specified, you must provide output name'.format(name))
            sys.exit(99)
    else:
        sys.stderr.write('{}: Warning - using ESRI Shapefile format because format was not provided\n'.format(name))
    ##Set default format if none
    if not ogrformat:
        ogrformat = "ESRI Shapefile"
    ##Check that each input exists and has same field names
    fieldnames = []
    if not echoonly:
        for shp in shapelist:
            try:
                if not names_match(shp,fieldnames):
                    sys.stderr.write('{}: File {} has mis-matched field names\n'.format(name, shp))
                    sys.exit(1)
            except Exception as exc:
                sys.stderr.write('{}: Exception raised when checking field names for file {}: {}\n'.format(name,shp,exc))
                sys.exit(1)
    if not shapelist:
        sys.stderr.write('{}: No shapefiles provided\n'.format(name))
        sys.exit(99)
    ##Now use ogr2ogr to combine shapefiles
    for shp in shapelist:
        try:
            cmd = ['ogr2ogr','-f',ogrformat,'-update','-append',]
            if namefield:
                nameval = os.path.splitext(os.path.basename(shp))[0]
                cmd.extend(['-sql',"select \'{}\' as {}, * from \"{}\"".format(nameval,namefield,nameval)])
            for o in ogropts:
                if o.find(" ") > -1:
                    cmd.extend(o.split())
                else:
                    cmd.append(o)
            cmd.extend([outname,shp])
            for o in lcopts:
                cmd.extend(['-lco',o])
            sys.stdout.write("{}\n".format(" ".join(cmd)))
            if not echoonly:
                subprocess.check_call(cmd)
        except Exception as exc:
            sys.stderr.write('{}: Exception raised when combining file {}: {}\n'.format(name,shp,exc))
            sys.exit(1)
    if kmlname:
        try:
            cmd = ['ogr2ogr','-f','KML','-t_srs','EPSG:4326',kmlname,outname]
            for o in kmlopts:
                cmd.extend(['-lco',o])
            sys.stdout.write("{}\n".format(" ".join(cmd)))
            if not echoonly:
                subprocess.check_call(cmd)
        except Exception as exc:
            sys.stderr.write('{}: Exception raised when creating kml {}: {}\n'.format(name,kmlname,exc))
            sys.exit(1)

if __name__ == '__main__':
    main()
