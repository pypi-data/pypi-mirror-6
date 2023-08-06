import numpy as np
import sqlite3 as lite
import re
from numpy import warnings
import scipy
import thread
from time import localtime, strftime
from datetime import date, timedelta
import datetime
from decimal import *
import urllib3
import time


def tracepatterns(pltp,whois,dtbse):
    datum=[dtbase,name,whois[3]]
    if whois[2]>whois[3]>pltp:
      thread.start_new_thread(publish, ("(BU) PHigh",datum,1))
    elif whois[2]<whois[3]<pltp:
      thread.start_new_thread(publish, ("(BD) PLow",datum,0))
    if whois[2]==whois[5]:
      thread.start_new_thread(publish, ("(H) THigh",datum,1))
    elif whois[2]==whois[6]:
      thread.start_new_thread(publish, ("(L) TLow",datum,1))
    return 0

def trend(symbol, databse, ltp, pltp):
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
         range = round(pphigh-pplow,2)
         pphigh1 = round(pphigh+range,2)
         pphigh2= round(pphigh1+range,2)
         pplow1=round(pplow-range,2)
         pplow2=round(pplow1-range,2)
         ppmid = round((pphigh+pplow)/2,2)
         ndatum = [symbol,databse[5:-3],ltp, pphigh2, pphigh1, pphigh, ppmid, pplow, pplow1, pplow2]
         datum = [symbol,databse[5:-3],ltp, pphigh, pplow, strftime("%H-%M-%S", localtime())]
         #if ltp > ppmid > pltp:
          #   _thread.start_new_thread(publish, ("(BU) PMid",datum,fetch(symbol,databse),1))
         #if ltp < ppmid < pltp:
          #   _thread.start_new_thread(publish, ("(BD) PMid",datum,fetch(symbol,databse),0))
         if ltp > pphigh > pltp:
             _thread.start_new_thread(publish, ("(BU) PHigh",datum,1))
         if ltp < pplow < pltp:
             _thread.start_new_thread(publish, ("(BD) PLow",datum,0))
         if ltp < pphigh < pltp:
             _thread.start_new_thread(publish, ("(R) PHigh",datum,0))
         if ltp > pplow > pltp:
             _thread.start_new_thread(publish, ("(R) PLow",datum,1))
         #if ltp > pphigh1 > pltp:
          #   _thread.start_new_thread(publish, ("(BU) PHigh1",datum,fetch(symbol,databse),1))
         #if ltp < pplow1 < pltp:
          #   _thread.start_new_thread(publish, ("(BD) PLow1",datum,fetch(symbol,databse),0))
         #if ltp < pphigh1 < pltp:
          #   _thread.start_new_thread(publish, ("(R) PHigh1",datum,fetch(symbol,databse),0))
         #if ltp > pplow1 > pltp:
          #   _thread.start_new_thread(publish, ("(R) PLow",datum,fetch(symbol,databse),1))
         #if ltp > pphigh2 > pltp:
          #   _thread.start_new_thread(publish, ("(BU) PHigh2",datum,fetch(symbol,databse),1))
         #if ltp < pplow2 < pltp:
          #   _thread.start_new_thread(publish, ("(BD) PLow2",datum,fetch(symbol,databse),0))
         #if ltp < pphigh2 < pltp:
          #   _thread.start_new_thread(publish, ("(R) PHigh2",datum,fetch(symbol,databse),0))
         #if ltp > pplow2 > pltp:
          #   _thread.start_new_thread(publish, ("(R) PLow2",datum,fetch(symbol,databse),1))
    except lite.OperationalError:
      con.close()
      return 0
def publish(what, contts, flag):
    dtta = what+" "+" ".join([str(i) for i in contts])+":"+str(flag)
    dtta = dtta.replace(" ", "%20")
    url5 = "http://charity-goldsax.rhcloud.com/Charity/getcontent.php?content="+dtta
    http = urllib3.PoolManager()
    #print( dtta)
    f=0
    while f!=1:
            try:
                r = http.request('GET', url5)
                r.release_conn()
            except urllib3.exceptions.MaxRetryError:
                time.sleep(5)
                http = urllib3.PoolManager()
                try:
                    r = http.request('GET', url5)
                    r.release_conn()
                except urllib3.exceptions.MaxRetryError:
                    print("Once retried dash and failed")
                    f=1
                    return 0
            except ConnectionResetError:
                time.sleep(5)
                http = urllib3.PoolManager()
                try:
                    r = http.request('GET', url5)
                    r.release_conn()
                except ConnectionResetError:
                    print("Once retried dash and failed")
                    f=1
                    return 0
            f = int(r.data.decode("latin-1"))
    return 0
    
def fetch(symbol, databse):
    con = lite.connect(databse)
    today = strftime("%Y-%m-%d", localtime())
    stmta = "SELECT PRIC FROM "+symbol+"table WHERE ONNN = '"+today+"';"
    cur = con.cursor()
    
    act = 0
    if 1:
      try:                               
        cur.execute(stmta)
        con.commit()
        
        row = cur.fetchall()
        con.close()
      except lite.OperationalError:
           return 0
       
      
    
    
    
    furr=[]
    
    for roo in row: 
        try:
                furr.append(float(re.sub('[^0-9.]+', '', str(roo))))
        except ValueError:
                act = 1
    
    if act != 1 and furr != []:
      tikk = givecoeffs(furr)
      """
      if tikk[0] ==1:
        
    
        connn = lite.connect('data/ANALYTICS.db')
        stmta = "INSERT INTO ANALYTIC(ASSET, PRIC, COMMENTS) VALUES ('"+symbol+"', '"+str(furr[-1])+"', '"+str(tikk[1])+"');"
        currr = connn.cursor()
        
        currr.execute(stmta)
      
        connn.commit()
        connn.close()
        """
        #print( "ASSET ", symbol, " from ", databse, " is ", furr[-1],tikk[1],"/n")
    try:
      return furr[-1],tikk[1]
    except IndexError:
      return 0,0
    act = 0

import numpy as np
from numpy import polyfit
from numpy import poly1d

previous =0
def givecoeffs(fur):
    x = np.array(np.linspace(1,len(fur),len(fur)))
    y = np.array(fur)
    
    z = np.polyfit(x,y,3)
    warnings.simplefilter('ignore', np.RankWarning)
    s = z.sum()
    t=[]
    for zz in z:
        t.append(zz)
    de = poly1d(np.array(t))
    det = np.polyder(de)
    dett = np.polyder(det)
    return 1, poly1d(np.array(t))
    #if (dett(len(fur)) < 0 and det(len(fur)) > 0) or (dett(len(fur)) > 0 and det(len(fur)) < 0) or det(len(fur)) ==0 or dett(len(fur))==0 :
     # return 1, poly1d(np.array(t))
    #else:
     # return 0,0
  
