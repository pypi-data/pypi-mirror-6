#!/usr/bin/python

# script creates gama-local input file from coordinates
# and theirs precisions - tag <coordinates>
#
# header fields
#    date: YYYY.MM.DD
#  format: posible fields - id ... point id
#                            x ... coordinate x
#                            y ... coordinate y
#                           sx ... stdev of coordinate x
#                           sy ... stdev of coordinate y
#                          cxy ... covariance of x and y coordinate
# units of coordinates and standard devitaion - meters
# unit of cxy is squared meters
# examples: id x y           - stdev is set by parameter --sigma-xy
#           id x y sx        - ellipse a = b
#           id x y sx sy     - ellipse om = 0
#           id x y sx sy cxy - full ellipse


import sys
#import datetime

from optparse import OptionParser
usage = "usage: %prog [opt] text_file_with_coordinates"
version = "%prog: v. 1.0"
parser = OptionParser(usage=usage, version=version)

parser.add_option("", "--sigma-xy", action="store", dest="sigmaXY",
                  help="standard deviation for all coordinates in meters")

(opt, args) = parser.parse_args()

if len(args) is 0:
    sys.exit("No file set")

if len(args) > 1:
    sys.exit("Give only one file")

sigmaXY = None
if opt.sigmaXY is not None:
    try:
        sigmaXY = float(opt.sigmaXY)
    except:
        sys.exit("Cannot convert value '%s' of parameter --sigma-xy to float" %
                 opt.sigmaXY)

try:
    file = open(args[0], 'rt')
except Exception, e:
    print >>sys.stderr, e
    sys.exit("Cannot open file %s" % args[0])

# read format and date from first two lines
format = None
date = None
for i in range(2):
    line = file.readline()
    fields = line.split()
    try:
        if fields[0][0:6] == "format":
            format = fields[1:]
            n_col = len(format)
            print >>sys.stderr, "Format: " + ", ".join(["%s" % i for i in format])
            if n_col < 3:
                sys.exit("Minimum 3 columns")
            if n_col > 6:
                sys.exit("Maximum 6 columns")
            if format[0] != "id":
                sys.exit("id must be first column")

        elif fields[0][0:4] == "date":
            date = fields[1]
            print >>sys.stderr, "Date: %s" % date
    except:
        pass

if format is None:
    print >>sys.stderr, "Format of rows is not set"
if date is None:
    print >>sys.stderr, "Date of epoch is not set"
if format is None or date is None:
    sys.exit(1)

# XML gama-local header and footer
header = """\
<?xml version="1.0" ?>
<!DOCTYPE gama-xml
  SYSTEM 'http://www.gnu.org/software/gama/gama-xml.dtd'>
<gama-local>
<network angles="left-handed" axes-xy="sw" epoch="1.1">
<parameters sigma-act="apriori"/>
<description>
[epoch]
date: %s
description: coordinates from file "%s", format "%s"
</description>
<points-observations>""" % (date, file.name, format)
footer = """\
</points-observations>
</network>
</gama-local>"""
print header

# read and print coordinates
points = []  # list of points id
covmat = []  # list of elements of covariance matrix
             # upper part of symetric matrix by rowx with band width bandWidth
if sigmaXY is None:
    bandWidth = 1
else:
    bandWidth = 0

print "<coordinates>"

for line in file:
    fields = line.split()
    points.append(fields[0])
    if len(fields) < n_col:
        sys.exit("Line %i: not enought numbers" % (len(points) + 2))
    if len(fields) > n_col:
        sys.exit("Line %i: too many numbers" % (len(points) + 2))
    #try:
    #    coords = [float(i) for i in fields]
    #except Exception, e:
    #    sys.exit("Line %i: cannot convert to float" % (n_points + 2))

    # print coords
    print '<point %s="%s" %s="%s" %s="%s"/>' % (format[0], fields[0],
                                                format[1], fields[1],
                                                format[2], fields[2])
    # compose covariance matrix
    if sigmaXY is not None:
        # diagonal matrix
        covmat.append((sigmaXY * 1e+3) ** 2)
        covmat.append((sigmaXY * 1e+3) ** 2)
    else:
        # matrix with two diagonals
        try:
            covmat.append((float(fields[format.index('sx')]) * 1e+3) ** 2)
        except:
            sys.exit("No sx nor --sigma-xy defined")
        try:
            covmat.append(float(fields[format.index('cxy')]) * 1e+6)
        except:
            covmat.append(0.0)
        try:
            covmat.append((float(fields[format.index('sy')]) * 1e+3) ** 2)
        except:
            covmat.append((float(fields[format.index('sx')]) * 1e+3) ** 2)
        covmat.append(0.0)

if sigmaXY is None:
    # delete last number in list covmat - is redundant
    covmat.pop()

# print covariance matrix
print '<cov-mat dim="%i" band="%i">' % (len(points) * 2, bandWidth)
print "  ".join(["%f" % i for i in covmat])
print "</cov-mat>"
print "</coordinates>"

# print points
print "\n".join(['<point id="%s" adj="xy"/>' % id for id in points])

print footer
