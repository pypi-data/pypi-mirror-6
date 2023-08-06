import sys
import _thread
import time
import gc
import sys
from GoldSaxLiveQuoteMachine import goldsaxlivequotemachine
from GoldSaxCreateTablesGFinance import goldsaxcreatetablesgfinance
from time import localtime, strftime
from GoldSaxEngineInitialize import goldsaxengineinitialize
databasestore = "AUSSIE"
location = "Australia"
def start():
        
        start1 = []
        sys.setrecursionlimit(1000)
        database = "data/"
        a,b,c=goldsaxengineinitialize.engineinitialize(location,databasestore)
        actionlist = a.splitlines()
        synamelist = c.splitlines()
        for listo in actionlist:
                lis = listo.split('", "')
                if lis[1] =='g' and lis[2].replace('"','')==databasestore+".db":
               
                        goldsaxcreatetablesgfinance.createtables(synamelist,lis[0].replace('"',''), database+lis[2].replace('"',''))
          

        markettime = {}

        mlist = b.splitlines()
        for line in mlist:
                items = line.split(", ")
                key, values = items[0], items[1]
                markettime[key] = values




        timetorun = 12000
        cycle = 1
        while("TRUE"):
        
                fileaslist = a.splitlines()
                a_lock = _thread.allocate_lock()
                b_lock =_thread.allocate_lock()
                thr = []
                jala=""
                with a_lock:
                        print("locks placed and GoldSax Market engine is running for the...", cycle)
                        for lines in fileaslist:
                                lisj = lines.split('", "')
                                mtime = markettime[lisj[2].replace('"','')]
                                mktime = mtime.split("-")
                                if mktime[1] < mktime[0]:
                                        righto = mktime[1].split(":")
                                        close = str(str(int(righto[0])+24)+":"+righto[1])
                        
                                
                        
                                else:
                                        close = mktime[1]
                        
                                rightnow = strftime("%H:%M", localtime())
                                if rightnow < strftime("04:00"):
                                        right = rightnow.split(":")
                                        rightnow = str(str(int(right[0])+24)+":"+right[1])
                                if (close > rightnow > mktime[0]):
                                
                                        thr.append(_thread.start_new_thread(goldsaxlivequotemachine.actionking, (lisj[1],b_lock, start1, lisj[0].replace('"',''),database+lisj[2].replace('"',''),0,synamelist,1,0,timetorun,jala) ))
                                
                                        time.sleep(0.00001)
                fileaslist=""
                gc.collect()
                print("locks placed and GoldSax Market engine is running for the....", cycle, " time..." )
        
                time.sleep(timetorun)
        
                print("locks released and GoldSax Market engine is restarting for the...", cycle, " time...")
                cycle = cycle + 1
