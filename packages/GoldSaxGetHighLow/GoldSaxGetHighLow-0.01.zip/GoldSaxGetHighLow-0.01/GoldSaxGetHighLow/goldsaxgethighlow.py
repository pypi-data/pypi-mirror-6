import sqlite3 as lite
from time import localtime, strftime
from datetime import date, timedelta
import datetime
from decimal import *
import time

class gethighlow:
  def renderit(symbol,databse):
    con = lite.connect(databse)
    today = strftime("%Y-%m-%d", localtime())
    yday = date.today() - timedelta(1)
    actualyesterday = yday.strftime("%Y-%m-%d")
    year,month,day = (int(x) for x in actualyesterday.split('-'))
    ans=datetime.date(year,month,day)
    if ans.strftime("%A")=="Sunday":
      yday = date.today() - timedelta(3)
      actualyesterday = yday.strftime("%Y-%m-%d")
    
    stmta = "SELECT MAX(PRIC),MIN(PRIC) FROM "+symbol+"table WHERE ONNN = '"+actualyesterday+"';"
    try:
       cur = con.cursor()
       act = 0                               
       cur.execute(stmta)
       con.commit()
        
       row = cur.fetchall()
       con.close()
       
       if type(row[0][0])==str or type(row[0][0])==int or type(row[0][0])==float:
         pphigh = round(float(row[0][0]),2)
         pplow = round(float(row[0][1]),2)
         return pphigh, pplow
    except lite.OperationalError:
      con.close()
      return 0,0
    return 0,0
