import urllib3
import string
from time import localtime, strftime
import time

class yahoofinancequote:
    
    def getquote(url):
            contents = []
            http = urllib3.PoolManager()
            try:
                r = http.request('GET', url)
                r.release_conn()
            except urllib3.exceptions.MaxRetryError:
                time.sleep(10)
                http = urllib3.PoolManager()
                try:
                    r = http.request('GET', url)
                    r.release_conn()
                except urllib3.exceptions.MaxRetryError:
                    print("Once retried Yahoo and failed")
                    return contents
            except ConnectionResetError:
                time.sleep(10)
                http = urllib3.PoolManager()
                try:
                    r = http.request('GET', url)
                    r.release_conn()
                except ConnectionResetError:
                    print("Once retried Yahoo and failed")
                    return contents
            f = r.data.decode("latin-1")
            a = f.split('\r\n')
            tstamp = strftime("%H:%M:%S", localtime())
            
            count = 0
            biz = len(a)
            for ass in a:
                if len(ass) > 0:
                    try:
                        v = ass.split(',')
                        contents.append([v[0].replace('"','').replace('.',''),strftime("%Y-%m-%d"),tstamp,float(re.sub('[^0-9.]+', '', v[1]))])
                    except IndexError:
                        print("index out")
                    except ValueError:
                        pass
                count = count+1
            return contents

