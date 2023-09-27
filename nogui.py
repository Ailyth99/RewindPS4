#!/usr/bin/env python

from __future__ import print_function
__version__ = "1.1.1"

import select, socket, sys,re
from datetime import datetime
import http.server as hserv
from socketserver import ThreadingMixIn
from check_version import *
import urllib.parse as urlparse
print_word = lambda wd: print(wd, end="\t", flush=True)
_ = lambda s: s.encode('utf-8')
import urllib3
urllib3.disable_warnings()



class ProxyHandler (hserv.BaseHTTPRequestHandler):
    __base = hserv.BaseHTTPRequestHandler
    __base_handle = __base.handle

    server_version = "TinyHTTPProxy/" + __version__
    rbufsize = 0                        

    #黑名单
    black_list = [""]

    def __init__(self, *args, **kwargs):
        self.black_list = [url for url in self.black_list if url]
        self.last_version_num = check_version(extract_cusa_id(self.target_json))[2]
        super().__init__(*args, **kwargs)

    def log_date_time_string(self):
        #日志时间格式
        now = datetime.now()
        return now.strftime('%m-%d %H:%M:%S:%f')[:-3]

    def handle(self):
        (ip, port) =  self.client_address
        if hasattr(self, 'allowed_clients') and ip not in self.allowed_clients:
            self.raw_requestline = self.rfile.readline()
            if self.parse_request(): self.send_error(403)
        else:
            self.__base_handle()

    def _connect_to(self, netloc, soc):
        i = netloc.find(':')
        if i >= 0:
            host_port = netloc[:i], int(netloc[i+1:])
        else:
            host_port = netloc, 80
        
        try: soc.connect(host_port)
        except socket.error as arg:
            try:
                msg = arg[1]
            except:
                msg = arg
            self.send_error(404, msg)
            return False
        return True

    def do_CONNECT(self):
        if any(bad_url in self.path for bad_url in self.black_list):
            self.send_error(403)
            print('------>>已屏蔽/Blocked：',self.path)
            return
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if self._connect_to(self.path, soc):
                self.log_request(200)
                self.wfile.write(_(self.protocol_version +
                                   " 200 Connection established\r\n"))
                self.wfile.write(_("Proxy-agent: %s\r\n" %
                                   self.version_string()))
                self.wfile.write(b"\r\n")
                self._read_write(soc, 300)
        finally:
            
            soc.close()
            self.connection.close()
        
        

    def do_GET(self):
        (scm, netloc, path, params, query, fragment) = urlparse.urlparse(
            self.path, 'http')
        if any(bad_url in self.path for bad_url in self.black_list):
            self.send_error(403)
            return

        if scm != 'http' or fragment or not netloc:
            self.send_error(400, "bad url %s" % self.path)
            return
        
        if self.last_version_num and self.target_json:
            self.replacements = [
                (re.compile(fr"-A{self.last_version_num}-.*\.json\b"), 
            self.target_json)
        ]
        else:
            self.replacements = []
        

        for pattern, replacement in self.replacements:
            if pattern.search(self.path):
                now=datetime.now().strftime('%m-%d %H:%M:%S:%f')[:-3]
                print(f"[{now}] - - 找到目标URL/Find target URL: ", self.path)  # 输出替换前的URL
                self.path = replacement
                print(f"[{now}] - - URL已替换为/Replaced URL: ", self.path)  # 输出替换后的URL
                break
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if self._connect_to(netloc, soc):
                self.log_request()
                soc.send(_("%s %s %s\r\n" % (
                    self.command,
                    urlparse.urlunparse(('', '', self.path, params, query, '')),
                    self.request_version)))
                self.headers['Connection'] = 'close'
                del self.headers['Proxy-Connection']
                for key_val in self.headers.items():
                    soc.send(_("%s: %s\r\n" % key_val))
                soc.send(b"\r\n")
                self._read_write(soc)
        finally:
            #print_word("bye")
            soc.close()
            self.connection.close()

    def _read_write(self, soc, max_idling=20):
        iw = [self.connection, soc]
        ow = []
        count = 0
        while True:
            count += 1
            (ins, _, exs) = select.select(iw, ow, iw, 3)
            if exs:
                break
            if ins:
                for i in ins:
                    if i is soc:
                        out = self.connection
                    else:
                        out = soc
                    data = i.recv(8192)
                    if data:
                        out.send(data)
                        count = 0
            #else:
                #print_word('')
            if count == max_idling:
                break

    do_HEAD = do_GET
    do_POST = do_GET
    do_PUT  = do_GET
    do_DELETE = do_GET
    do_OPTIONS = do_GET

class ThreadingHTTPServer (ThreadingMixIn, hserv.HTTPServer):
    pass

def main(argv):
    if argv[1:] and argv[1] in ('-h', '--help'):
        print(argv[0], "[port [allowed_client_name ...]]")
    else:
        server_address = ('', int(argv[1]) if argv[1:] else 8080)
        if argv[2:]:
            allowed = []
            for name in argv[2:]:
                client = socket.gethostbyname(name)
                allowed.append(client)
                print("Accept: %s (%s)" % (client, name))
            ProxyHandler.allowed_clients = allowed
        else:
            print("Any clients will be served...")
        print("-------------\n【重要提示】请在下方输入正确的目标版本json链接。比如：http://gs2.ww.prod.dl.playstation.net/gs2/ppkgo/prod/CUSA31579_00/3/f_cf39347e65718377680b86477d9b6459737f003afe295e7bf979901187370bf7/f/UP3463-CUSA31579_00-6937190672078757-A0103-V0100.json\n-->获取任何版本的json链接，请访问：https://orbispatches.com/\n-------------")
        print("【Important】Please enter the correct target version json link below. For example: http://gs2.ww.prod.dl.playstation.net/gs2/ppkgo/prod/CUSA31579_00/3/f_cf39347e65718377680b86477d9b6459737f003afe295e7bf979901187370bf7/f/UP34 63-CUSA31579_00-6937190672078757-A0103-V0100.json\n -->To get the json link for any version, please visit: https://orbispatches.com/\n-------------")

        target_json = input("请粘贴json地址/please paste json link：")
        while not target_json.startswith("http://gs2.ww.prod.dl.playstation.net/gs2/ppkgo/prod/") or not target_json.endswith(".json"):
            print("json链接不正确，请重新输入/Invalid URL, please try again.")
            target_json = input("请粘贴json地址/please paste json link：")

        ProxyHandler.target_json = target_json
        httpd = ThreadingHTTPServer(server_address, ProxyHandler)
        (host, port) = httpd.socket.getsockname()
        
        i=check_version(extract_cusa_id(target_json))        
        print("\n目标游戏/Target game：{} {}，降级版本/Downgrade version：{}".format(i[0], i[1], extract_version(target_json)))
        print("\n代理服务器启动/Proxy server started","\n本机IP/Local IP：",get_local_ip(), ",端口/Port：", port)
        print("请在主机设置好代理，再开始下载游戏/Please set up the proxy on the console before starting the game download.\n------------")

        httpd.serve_forever()

if __name__ == '__main__':
    main(sys.argv)