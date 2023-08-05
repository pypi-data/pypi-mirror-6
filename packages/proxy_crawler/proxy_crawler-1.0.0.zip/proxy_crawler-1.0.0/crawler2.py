#coding="uft-8"
import urllib2
import re
import threading
import time
'''
htttp://www.cnproxy.com/proxy1.html
'''
proxylist1=[]
#portdicts={"v":"3","m":"4","a":"2","l":"9","q":"0","b":"5","i":"7","w":"6","r":"8","c":"1"}
def get_proxy_from_cnproxy():
    global proxylist1
    global portdicts
    p=re.compile(r'''\s+?<tr data-id=".+?" data-type="transparent">\s+?<td class="tcenter">&nbsp;.+?&nbsp;</td>\s+?<td>(.+?)</td>\s+?<td>(.+?)</td>\s+?<td>\s+?<img border=".+?" width=".+?" height=".+?" alt=".+?" src=".+?" />&nbsp;\s+?<a href=".+?" title=".+?">(.+?)</a>\s+?''')
    target=r"http://pachong.org/"
    req=urllib2.urlopen(target)
    print target
    result = req.read()
    print result
    matchs=p.findall(result)
    print matchs
    for row in matchs:
        ip=row[0]
        port=row[1]
        #port=map(lambda x:portdicts[x], port.split("+"))
        #port=''.join(port)
        #agent=row[2]
        addr=row[2]
            
        l=[ip,port,addr]
        proxylist1.append(l)
        print l
            
class ProxyCheck(threading.Thread):
    def __init__(self,proxylist,fname):
        threading.Thread.__init__(self)
        self.proxylist=proxylist
        self.timeout=5
        self.test_url="http://www.baidu.com/"
        self.test_str="030173"
        self.checkedProxyList=[]
        self.fname=fname
    def checkProxy(self):
        cookies=urllib2.HTTPCookieProcessor()
        for proxy in self.proxylist:
            proxy_handler=urllib2.ProxyHandler({"http":r'http://%s:%s'%(proxy[0],proxy[1])})
            print 'http://%s:%s'%(proxy[0],proxy[1])
            opener=urllib2.build_opener(cookies,proxy_handler)
            #opener.addheaders=["User-Agent","Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36"]
            urllib2.install_opener(opener)
            t1=time.time()
            try:
                print self.test_url
                #req=urllib2.urlopen(self.test_url,timeout=self.timeout)
                #result=req.read()
                result=urllib2.urlopen(self.test_url,timeout=self.timeout).read()                
                print result
                timeusd=time.time()-t1
                pos=result.find(self.test_str)
                if pos>1:
                    self.checkedProxyList.append((proxy[0],proxy[1],proxy[2],timeusd))
                else:
                    continue
            except Exception,e:
                print e.message
                continue
    def sort(self):
        sorted(self.checkedProxyList,cmp=lambda x,y:cmp(x[3],y[3]))
    def save(self):
        f=open(self.fname,'w')
        for proxy in self.checkedProxyList:
            f.write("%s:%s\t%s\t%s\n"%(proxy[0],proxy[1],proxy[2],str(proxy[3])))
        f.close()
    def run(self):
        self.checkProxy()
        self.sort()
        self.save()
if __name__=="__main__":    
    get_proxy_from_cnproxy()
    
    t1=ProxyCheck(proxylist1, "proxylist_pachong.txt")
    t1.start()