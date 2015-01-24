import sqlite3 as lite
import os.path
import sys
import argparse

def main(dbfile):
    thelist = []
    con = lite.connect(dbfile)
    with con:
        cur = con.cursor()
        cur.execute("SELECT t.*, a.registration, a.ICAOTypeCode, a.modescountry FROM trackslog t JOIN Aircraft a ON (t.modes=a.modes) WHERE lat>0")
        for row in cur.fetchall():
            print ";".join([str(x) for x in row])

if __name__=="__main__":
    parser = argparse.ArgumentParser("Output dump1090 database in .csv format")
    parser.add_argument("dbfile", nargs="?", help="SQlite database file to use (default: %(default)s)", default="basestation.sqb")
    args = parser.parse_args()

    if not os.path.isfile(args.dbfile):
        print "ERROR: file '{0}' does not exist\n".format(args.dbfile)
        parser.print_help()
        sys.exit(1)

    main(args.dbfile)

