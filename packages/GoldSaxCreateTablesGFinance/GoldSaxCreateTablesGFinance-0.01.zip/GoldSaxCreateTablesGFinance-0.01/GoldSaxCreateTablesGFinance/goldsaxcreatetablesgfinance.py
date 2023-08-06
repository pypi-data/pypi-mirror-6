from goldsaxgfinancequote import *
import sqlite3 as lite
import string
import time
import re
print ("Market Starts.......")

def pullprocess(ass):
        sds = goldsaxgfinancequote.getquote(ass)
        return sds
def createtables(url,dbase):
        f = pullprocess(url)
        print ("Database ", dbase, " Tablespace check Started.........")
        con = lite.connect(dbase)
        with open('conf/symbolname.conf') as fille:
            actionlist = fille.read().splitlines()
        fille.close()
        for fuck in f:
            name = fuck[0]
            for act in actionlist:
                actor = act.split("=")        
                if name==actor[0]:
                        name = actor[1]
            name = re.sub('[^a-zA-Z]+', '', name)
            
            stmt = "CREATE TABLE IF NOT EXISTS "+name+"table(ONNN TEXT, ATTT TEXT, PRIC REAL)"
            cur = con.cursor()
            try:
                    cur.execute(stmt)
            except lite.OperationalError:
                    print(fuck[0],stmt)
                    time.sleep(0.5)
                    print("Database ", dbase, " Tablespace check Failed.........")
            
        con.commit()
        con.close()
        time.sleep(2)
        print ("Database ", dbase, " Tablespace check finished.........")

    
    
