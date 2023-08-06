import urllib3
import string
import re
from time import localtime, strftime

class goldsaxgfinancequote:
    
    def getquote(url):
            http = urllib3.PoolManager()
            try:
                contents = []
                r = http.request('GET', url)
                r.release_conn()
            except urllib3.exceptions.MaxRetryError:
                return contents
            except ConnectionResetError:
                return contents
            f = r.data.decode("latin-1")
            a = f.split('"t" : "')
            tstamp = strftime("%H:%M:%S", localtime())
            count = 0
            
            for ass in a:
                if count > 0:
                    v = ass.split('"\n,"e" : "')
                    h = ass.split(',"l" : "')
                    j = h[1].split('"\n,"l_')
                    #filename = strftime("%Y-%m-%d", localtime())+"_"+v[0]+".csv"
                    #text_file = open(filename, "a")
                    #text_file.write(tstamp+", "+j[0]+"\n")
                    #text_file.close()
                    try:
                        contents.append([v[0],strftime("%Y-%m-%d"),tstamp,float(re.sub('[^0-9.]+', '', j[0]))])
                    except ValueError:
                        pass
                count = count+1
            return contents

