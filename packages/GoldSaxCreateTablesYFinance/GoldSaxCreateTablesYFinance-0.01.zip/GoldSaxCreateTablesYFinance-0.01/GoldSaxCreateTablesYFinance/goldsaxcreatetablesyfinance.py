from GoldSaxYFinanceQuote import goldsaxyfinancequote
import sqlite3 as lite
import string
import time
import re

print ("Market Place Starts.......")

def pullprocess(ass):
        sds = goldsaxyfinancequote.getquote(ass)
        return sds
def createtables(actionlist,url,dbase):
        f = pullprocess(url)
        print ("Database ", dbase," Started to be checked for tablespaces.........")
        con = lite.connect(dbase)
            
        for fuck in f:
            name = fuck[0]
            for act in actionlist:
                actor = act.split("=")        
                if name==actor[0]:
                        name = actor[1]
            name = re.sub('[^a-zA-Z]+', '', name)
            name = name.replace("^","")
            name = name.replace("-","")
            name = name.replace(" ","")
            name = name.replace("=","")
            numerals = [0,1,2,3,4,5,6,7,8,9]
            for num in numerals:
                    name = name.replace(str(num),"")
            stmt = "CREATE TABLE IF NOT EXISTS "+name+"table(ONNN TEXT, ATTT TEXT, PRIC REAL)"
            cur = con.cursor()
            cur.execute(stmt)
            
        con.commit()
        con.close()
        time.sleep(5)
        print ("Database ", dbase," finished checking for tablespaces.........")

    
    
