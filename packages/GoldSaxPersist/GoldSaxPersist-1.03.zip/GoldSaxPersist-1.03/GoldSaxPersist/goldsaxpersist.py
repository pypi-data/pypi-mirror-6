import sqlite3 as lite
def push(loc,dbs,stt):
      try:
        loc.acquire()
        con = lite.connect(dbs)                                   
        con.executescript(stt)
        con.commit()
        con.close()
        loc.release()
        return 0
      except lite.OperationalError:
        con.commit()
        con.close()
        loc.release()
        print(dbs, "script error", len(stt))
        return 0
