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

    
    def __init__(self, *args, **kwargs):
        self.black_list = kwargs.pop('black_list', [])
        if 'target_json' in kwargs:
            self.target_json = kwargs.pop('target_json')
            self.last_version_num = check_version(extract_cusa_id(self.target_json))[2]
        else:
            self.target_json = None
            self.last_version_num = None
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
            print('------>>Blocked:',self.path)
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
                print(f"[{now}] - - Find target json: ", self.path)  # 输出替换前的URL
                self.path = replacement
                print(f"[{now}] - - Replaced json: ", self.path)  # 输出替换后的URL
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
    print("""
    ____               _           ______  _____ __ __
   / __ \___ _      __(_)___  ____/ / __ \/ ___// // /
  / /_/ / _ \ | /| / / / __ \/ __  / /_/ /\__ \/ // /_
 / _, _/  __/ |/ |/ / / / / / /_/ / ____/___/ /__  __/
/_/ |_|\___/|__/|__/_/_/ /_/\__,_/_/    /____/  /_/    

                                v0.9 NoGUI Version 
""")
    while True:
        mode = input(f"""Please choose mode
Mode1 -- Download Specified Version (works on PS4/PS5 console)
Mode2 -- Block Patches, Download 1.0 Base Game (only works on PS4 console)
Enter 1 or 2:""").strip()
        if mode == '1':
            json_info='Please paste the JSON link of the patch you need to download:\n'
            target_json = input(json_info)
            while not target_json.startswith("http://gs2.ww.prod.dl.playstation.net/gs2/ppkgo/prod/") or not target_json.endswith(".json"):
                print("Invalid URL, please try again:")
                target_json = input()
            black_list = []
            break
        elif mode == '2':
            target_json = None
            black_list = ["gs-sec.ww.np.dl.playstation.net"]
            break
        else:
            print("----------\nInvalid mode selected. Enter 1 or 2 to select mode\n----------")

    port = int(argv[1]) if argv[1:] else 8080  # 默认端口8080
    while True:
        if check_port(port):
            print(f"{tr('Port')} {port} {tr('is already in use')}")
            while True:
                port_input = input(tr("Please enter another port (1024-65535): "))
                try:
                    port = int(port_input)
                    if 1024 <= port <= 65535:
                        break  
                    else:
                        print(tr("Port number must be between 1024 and 65535."))
                except ValueError:
                    print(tr("Invalid input. Please enter an integer."))
        else:
            break  # 端口未被占用且合法

    server_address = ('', port)
    tprint(f"Model{mode} Selected")
    
    if mode == '1':
        httpd = ThreadingHTTPServer(server_address, lambda *args, **kwargs: ProxyHandler(*args, target_json=target_json, black_list=black_list, **kwargs))
    else:  
        httpd = ThreadingHTTPServer(server_address, lambda *args, **kwargs: ProxyHandler(*args, black_list=black_list, **kwargs))

    if mode == '1' and target_json:
        i = check_version(extract_cusa_id(target_json))
        if i:  
            game_info="Game Name: {}\nGame ID: {}\nDowngrade version: {}".format(i[1], i[0], extract_version(target_json))
            print(game_info)

    print("\nProxy server started", "\nProxy IP: ", get_local_ip(), " Port: ", server_address[1])
    print("**The logs might show some errors, but as long as the download keeps going, just ignore those errors.")
    print("Please set up the proxy network in your console's network settings, before starting the game download.\n------------")
    
    httpd.serve_forever()

if __name__ == '__main__':
    main(sys.argv)