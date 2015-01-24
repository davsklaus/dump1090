import sqlite3 as lite
import math
import datetime
import os.path
import sys
import argparse

# constants and globals
gFollowICAO='XX'
gFollowDist=99.9
gDidSnap=0
gFileBase=' '

cRadiusOfEarth = 6371;
cFeetToKm = 0.0003048
# Home position
cHomeLat1=63.3
cHomeLon1=10.3

# Code from the excellent "Pi Plane Project"
# http://simonaubury.com/the-pi-plane-project1-introduction/
def haversine(pLatitude, pLongitude, pFeet):
    lat2=pLatitude
    lon2=pLongitude
    #pFeet = 1000

    f1 = math.radians(cHomeLat1);
    f2 = math.radians(lat2);
    delta_f = math.radians(lat2-cHomeLat1);
    delta_g = math.radians(lon2-cHomeLon1);
    a = math.sin(delta_f/2) * math.sin(delta_f/2) +  math.cos(f1) * math.cos(f2) *    math.sin(delta_g/2) * math.sin(delta_g/2);
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a));
    dist_km = cRadiusOfEarth * c;
    brng_r=math.atan2(
      math.sin(lon2-cHomeLon1) * math.cos(lat2)
    , math.cos(cHomeLat1)*math.sin(lat2)-math.sin(cHomeLat1)*math.cos(lat2)*math.cos(lon2-cHomeLon1)
    )

    brng_d=(360.0 - math.degrees(brng_r))%360.0
    azmth=math.degrees(math.atan(pFeet*cFeetToKm / dist_km))

    return dist_km, brng_d

def finddates(dbfile):
    thelist = []
    con = lite.connect(dbfile)
    with con:
        cur = con.cursor()
        cur.execute("SELECT distinct(date(last_update)) from trackslog where lat>0")
        for row in cur.fetchall():
            thelist.append(row[0])
    return thelist

def pretty_print(row):
    for field in row:
        if type(field) == float:
            print "%4.3f" % field,
        else:
            print str(field),
    print ""

def main(dbfile, datetofind):
    thelist = []
    con = lite.connect(dbfile)
    with con:
        cur = con.cursor()

        cur.execute("SELECT modes, lat, lon, alt, last_update FROM trackslog WHERE lat>0 and date(last_update)=date('%s')" % datetofind)
        for row in cur.fetchall():
            modes, lat, lon, alt, last_update = row
            dist, az = haversine(lat, lon, alt)
            #print alt, lat, lon, dist, az
            thelist.append((dist, az, lat, lon, alt, last_update))
    return thelist

def main2(csvfile):
    thelist = []
    f=open(csvfile, "r")
    for line in f.readlines():
        values = line.strip().split('|')
        modes = values[1]
        alt = int(values[2])
        lat = float(values[4])
        lon = float(values[5])
        if lon > 0:
            dist, az = haversine(lat, lon, alt)
            #print alt, lat, lon, dist, az
            thelist.append((dist, az, lat, lon, alt, modes))

    return thelist

if __name__=="__main__":
    parser = argparse.ArgumentParser("Simple analysis of dump1090 database")
    parser.add_argument("dbfile", nargs="?", help="SQlite database file to use (default: %(default)s)", default="basestation.sqb")
    args = parser.parse_args()

    if not os.path.isfile(args.dbfile):
        print "ERROR: file '{0}' does not exist\n".format(args.dbfile)
        parser.print_help()
        sys.exit(1)

    available_dates = finddates(args.dbfile)

    print "# (dist, az, lat, lon, alt, last_update)"
    for adate in available_dates:
        thelist = main(args.dbfile, adate)


        furthest = max(thelist, key=lambda x: x[0])
        print adate, "longest distance is",
        pretty_print(furthest)

    today = datetime.date.today().isoformat()
    thelist = main(args.dbfile, today)
    #thelist = main2("dump.csv")

    # Show to 25 entries
    thelist.sort(key=lambda x: -x[0])

    print "Furthest away points today:"
    for fields in thelist[:25]:
        pretty_print(fields)
        #print "; ".join([str(x).ljust(10) for x in fields])
