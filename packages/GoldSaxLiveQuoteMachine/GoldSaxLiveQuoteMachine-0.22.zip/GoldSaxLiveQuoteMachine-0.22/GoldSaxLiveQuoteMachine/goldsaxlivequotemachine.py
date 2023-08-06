from GoldSaxGFinanceQuote import goldsaxgfinancequote
from GoldSaxYFinanceQuote import goldsaxyfinancequote
from GoldSaxGetHighLow import goldsaxgethighlow
import string
import gc
import time
import math
import _thread
from random import randint
from GoldSaxPersist import goldsaxpersist
import re

def actionking(att,lck, tempf, stocklist, dbase, attmt,actionlist,cycle,timeatpresent,timetotake,sqlstatements):
    if tempf == []:
        timeatpresent = time.clock()
    if (time.clock() - timeatpresent) > timetotake:
      with lck:
        _thread.start_new_thread(goldsaxpersist.push,(lck,dbase,sqlstatements))
        return 0
    f = pullprocess(stocklist,att)
    if tempf == []:
          datastore={}
          namestore={}
          for asset, day, instant, lastprice in f:
            name = asset
            qname = asset
            for act in actionlist:
               actor = act.split("=")        
               if name==actor[0]:
                     qname=actor[0]
                     name = actor[1]
            name = re.sub('[^a-zA-Z]+', '', name)
            namestore[qname]=name
            high, low = goldsaxgethighlow.renderit(name, dbase)
            datastore[name] = [day, instant, float(lastprice),high,low]
          actionlist=""    
    sorter = []
    if tempf!=[]:
        namestore=tempf[0]
        datastore=tempf[1]
        for asset, day, instant, lastprice in f:
            name = namestore[asset]
            
            values=datastore[name]
            if values[2]!=lastprice:
                if values[3] > lastprice > values[4]:
                    print()
                if values[3] < lastprice < values[4]:
                    print()
                datastore[name] = [day, instant, float(lastprice),values[3],values[4]]
                stmt = "INSERT INTO "+name+"table(ONNN, ATTT, PRIC) VALUES ('"+day+"', '"+instant+"', "+str(round(lastprice,2))+");"
                sorter.append(name)
                sqlstatements = sqlstatements+" "+stmt
    tempf=namestore,datastore
    if sorter != []:
        attmt = 0
    if tempf != [] and sorter == [] and attmt == 4:
        gc.collect()
        print(dbase,"exhausted trying...exchange closed")
        return 0
    if tempf != [] and sorter == [] and attmt == 3:
        time.sleep(60)
        gc.collect()
        attmt = 4
        
    if tempf != [] and sorter == [] and attmt == 2:
        time.sleep(30)
        gc.collect()
        attmt = 3
        
    if tempf != [] and sorter == [] and attmt == 1:
        time.sleep(10)
        gc.collect()
        attmt = 2
        
    if tempf != [] and sorter == []:
        time.sleep(5)
        attmt = 1     
        gc.collect()
    tmppf=""
    sorter=""
    time.sleep(randint(0,2))
    gc.collect()
    if sqlstatements!="" and cycle==999999:
      with lck:
        _thread.start_new_thread(goldsaxpersist.push,(lck,dbase,sqlstatements))
      sqlstatements=""
    cycle = cycle + 1
    return actionking(att,lck,tempf, stocklist,dbase, attmt,actionlist,cycle,timeatpresent,timetotake,sqlstatements)
def pullprocess(ass,dee):
    if dee=="g":
        sds = goldsaxgfinancequote.getquote(ass)
        return sds
    elif dee=="y":
        sds = goldsaxyfinancequote.getquote(ass)
        return sds

