import sqlite3 as lite

def main(dbfile):
    thelist = []
    con = lite.connect(dbfile)
    with con:
        cur = con.cursor()
        cur.execute("SELECT t.*, a.registration, a.ICAOTypeCode, a.modescountry FROM trackslog t JOIN Aircraft a ON (t.modes=a.modes) WHERE lat>0")
        for row in cur.fetchall():
		print ";".join([str(x) for x in row])

if __name__=="__main__":
    main("../basestation.sqb")
