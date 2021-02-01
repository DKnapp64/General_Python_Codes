#!/bin/env python3
import sys
import os
from matplotlib import pyplot as plt
from matplotlib import cm
import pandas
import numpy
import argparse

def split_integers(arglist):
    indices = []
    parts = arglist.split(",")
    for p in parts:
        stp = p.strip()
        if stp == "":
            continue
        dashparts = stp.split("-")
        if len(dashparts) == 1:
            indices.append(int(dashpart[0]))
        elif len(dashparts) == 2:
            start = int(dashparts[0])
            end = int(dashparts[1])
            if end < start:
                indices.extend([i for i in range(start,end-1,-1)])
            else:
                indices.extend([i for i in range(start,end+1)])
        else:
            raise RuntimeError("Could not extract integer list from {}".format(stp))
    return indices

def main():
    parser = argparse.ArgumentParser(description='Read in CSV spectral library and plot into image file')
    parser.add_argument('--width','-w',help='width of output image in inches',type=float,default=10.0)
    parser.add_argument('--height','-t',help='height of output image in inches',type=float,default=8.0)
    parser.add_argument('--xmin','--wlmin',help='Minimum X value (wavelength)',type=float,default=numpy.nan)
    parser.add_argument('--xmax','--wlmax',help='Maximum X value (wavelength)',type=float,default=numpy.nan)
    parser.add_argument('--ymin','--respmin',help='Minimum Y value (wavelength)',type=float,default=numpy.nan)
    parser.add_argument('--ymax','--respmax',help='Mayimum X value (wavelength)',type=float,default=numpy.nan)
    parser.add_argument('--sep','-s',help='Field separator',type=str,default=',')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--include',help='comma-separated list of library numbers to include in the plot, ranges are allowed, eg. "1,2,6-7"',type=str,default="")
    group.add_argument('--exclude',help='comma-separated list of library numbers to exclude in the plot, ranges are allowed, eg. "1,2,6-7"',type=str,default="")
    parser.add_argument('--cmap',help='matplotlib.cm color pallete name',type=str,default='Dark2')
    parser.add_argument('--xlab',help='Label for X axis',type=str,default='Wavelength (nm)')
    parser.add_argument('--ylab',help='Label for Y axis',type=str,default='Reflectance')
    parser.add_argument('--dpi','-d',help='Dots per inch of output image',type=float,default=200.0)
    parser.add_argument('--trans','-x',help='Use transparent background',action="store_true")
    parser.add_argument('--noheader','-l',help='Specify no header row',action="store_true")
    parser.add_argument('input',type=str)
    parser.add_argument('output',type=str)

    args = parser.parse_args()

    fig, ax = plt.subplots(figsize=(args.width,args.height))


    ##Get CSV file
    print("Opening library {}".format(args.input))
    if args.noheader:
        csvdat = pandas.read_csv(args.input,header=None)
        names = ["Spectrum{}".format(i) for i in csvdat.columns.values[1:]]
    else:
        csvdat = pandas.read_csv(args.input)
        names = csvdat.columns.values[1:]

    #Get user-specified libraries if any
    user_selected = [i for i in range(1,len(names)+1)]
    if args.include != "":
        user_selected = split_integers(args.include)
    elif args.exclude != "":
        excludes = split_integers(args.include)
        user_selected = [i for i in range(1,len(names)+1) if i not in excludes]
    print("Keeping the following spectra")
    for i in user_selected:
        print("({}), {}".format(i,names[i-1]))


    ##Get ranges of wavelengths (must be field 0) and Y
    wlrange = [csvdat.iloc[:,0].min(), csvdat.iloc[:,0].max()]
    print("Library covers wavelengths from {} to {}".format(*wlrange))
    resprange = [0.0,csvdat.iloc[:,user_selected].max().max()]
    print("Maximum reflectance value {}".format(resprange[1]))
    if not numpy.isnan(args.xmin) and args.xmin > wlrange[0]:
        wlrange[0] = args.xmin
    if not numpy.isnan(args.xmax) and args.xmax < wlrange[1]:
        wlrange[1] = args.xmax
    if not numpy.isnan(args.ymin) and args.ymin > resprange[0]:
        resprange[0] = args.ymin
    if not numpy.isnan(args.ymax) and args.ymax > resprange[1]:
        resprange[1] = args.ymax
        
    ##Create a color scheme
    cmap = cm.get_cmap(args.cmap)(numpy.arange(len(user_selected))/float(len(user_selected)))

    ##Get row indices of entries within specified wl range
    wrange = numpy.where(numpy.logical_and(csvdat.iloc[:,0] >= wlrange[0],csvdat.iloc[:,0] <= wlrange[1]))[0]
    if wrange.size < 1:
        raise RuntimeError("No spectrum values between {} and {} nm".format(*wlrange))
    else:
        print("Plotting spectra between {} and {} nm".format(*wlrange))


    ##Ok, start plotting
    for ci, i in enumerate(user_selected):
        ax.plot(csvdat.iloc[wrange,0],csvdat.iloc[wrange,i],c=cmap[ci],label=names[i-1])
    ax.set(xlabel=args.xlab,ylabel=args.ylab)
    ax.legend()

    plt.savefig(args.output, dpi=args.dpi, bbox_inches='tight')
    print("Plot saved as {}".format(args.output))

if __name__ == '__main__':
  main()
