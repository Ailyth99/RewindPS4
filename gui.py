#!/usr/bin/env python
"""
Created on Tue Aug 29 14:45:06 2023
@author: Sylph
"""
from __future__ import print_function
import pkg_resources
__version__ = "1.1.1"
from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtGui import QPixmap,QIcon
from PyQt5.QtWidgets import QGraphicsScene,QMessageBox
from PyQt5.QtCore import Qt,QTimer
from UIW import Ui_Dialog
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


#Server本体
class ProxyHandler (hserv.BaseHTTPRequestHandler):
    __base = hserv.BaseHTTPRequestHandler
    __base_handle = __base.handle

    server_version = "TinyHTTPProxy/" + __version__
    rbufsize = 0                        

    def __init__(self, *args, **kwargs):
        self.data_transferred = 0 #数据传输量
        self.black_list = kwargs.pop('black_list', []) #黑名单
        target_json = self.target_json
        if target_json:
            self.last_version_num = check_version(extract_cusa_id(target_json))[2]
        else:
            self.last_version_num = None  
        super().__init__(*args, **kwargs)

    def log_date_time_string(self):
        now = datetime.now()
        return now.strftime('%m-%d %H:%M:%S')

    def log_message(self, format, *args):
        if ".pkg" not in self.path:
            sys.stderr.write("%s [%s] \"%s\"\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))

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
            tprint(f"<font color='#f51c7a'>已屏蔽版本检查</font>")
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
        data_length = 0
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
                now=datetime.now().strftime('%m-%d %H:%M:%S')
                original_version = extract_version(self.path)
                print(f"{self.client_address[0]}[{now}] >> <font color='#ffaa00'><b>找到最新版本:</b></font><font color='#80ffe3'>[{original_version}]</font>{self.path}")  # 输出替换前的URL

        # 检查两个URL是否属于同一个游戏
                original_cusa_id = extract_cusa_id(self.path)
                replacement_cusa_id = extract_cusa_id(replacement)
                if original_cusa_id != replacement_cusa_id:
                    tprint(f"<br><font color='#f54b4e'>########################################<br><b>错误：不属于同一个游戏ID<br>需要下载的游戏CUSA ID是{original_cusa_id}，<br>替换的版本对应CUSA ID是{replacement_cusa_id}<br>PS5:报错CE-107893-8<br>PS4:直接报错无法下载</b><br>########################################</font>")
                    #break

                replacement_version = extract_version(replacement)
                self.path = replacement
                print(f"{self.client_address[0]}[{now}] >> <font color='#ffaa00'><b>已映射版本为:</b></font><font color='#80ffe3'>[{replacement_version}]</font>{self.path}")  # 输出替换后的URL
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
           
            soc.close()
            self.connection.close()
            if ".pkg" in self.path:
                now=datetime.now().strftime('%m-%d %H:%M:%S')
                print(f"{self.client_address[0]} [{now}][{self.data_transferred / 1024 / 1024:.2f}MB]GET {self.path}")  # 输出包含数据传输量的日志
            self.data_transferred = 0  # 重置数据传输量    

        

    def _read_write(self, soc, max_idling=20):
        now=datetime.now().strftime('%m-%d %H:%M:%S')
        iw = [self.connection, soc]
        ow = []
        count = 0
        
        while True:
            count += 1
            try:
                (ins, _, exs) = select.select(iw, ow, iw, 3)
                if exs:
                    break
                if ins:
                    for i in ins:
                        if i is soc:
                            out = self.connection
                        else:
                            out = soc
                        try:
                            data = i.recv(8192)
                        except (ConnectionAbortedError, ConnectionResetError):
                            print(f"{self.client_address[0]}[{now}]>> 链接被中断")
                            return
                        if data:
                            out.send(data)
                            count = 0
                            self.data_transferred += len(data) # 更新数据传输量
            except (ConnectionAbortedError, ConnectionResetError):
                print(f"{self.client_address[0]}[{now}]>> 链接被中断")
                break
            if count == max_idling:
                break

    do_HEAD = do_GET
    do_POST = do_GET
    do_PUT  = do_GET
    do_DELETE = do_GET
    do_OPTIONS = do_GET

class ThreadingHTTPServer (ThreadingMixIn, hserv.HTTPServer):
    pass

class LogHandler(QtCore.QObject):
    signal = QtCore.pyqtSignal(str)
    whitelist_words = ["playstation", ">>"]
    cusa_pattern = re.compile(r'(CUSA\d{5})')  
    ip_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')  
    time_pattern = re.compile(r'\[\d{2}-\d{2} \d{2}:\d{2}:\d{2}]')  
    version_pattern = re.compile(r'-A(\d{4})-')  
    data_trans=re.compile( r'\[(\d+\.\d+MB)\]')

    def write(self, text):
        if any(word in text for word in self.whitelist_words) and text.strip(): 
            text = text.replace('""', '').replace('HTTP/1.1" 200 -"', '').replace(':443', '').replace('CONNECT', '')
            match = self.cusa_pattern.search(text)
            cusa_match = match if match else None

            match = self.version_pattern.search(text)
            version_match = match if match else None

            ppkgo = "ppkgo" in text
            appkgo = "appkgo" in text
            pkg = "pkg" in text
            nojson="json" not in text
            noDP="-DP.pkg" not in text
            nopng=".png" not in text
            PPSA="PPSA"  in text
            match = self.ip_pattern.search(text)
            if match:
                ip = match.group(1)
                green_ip = f"<font color='#b2f5a7'><b>{ip}</b></font>"
                text = text.replace(ip, green_ip)

            match = self.time_pattern.search(text)
            if match:
                time = match.group(0)
                purple_time = f"<font color='#9ca5f5'>{time}</font>"
                text = text.replace(time, purple_time)

            match = self.data_trans.search(text)
            if match:
                trans = match.group(0)
                colored_trans = f"<font color='#c3f707'>{trans}</font>"
                text = text.replace(trans, colored_trans)

            if ppkgo and cusa_match and version_match and pkg and nojson and noDP and nopng:
                version = version_match.group(1)
                formatted_version = f"{version[:2]}.{version[2:]}"
                text = text.replace("GET", "<b><font color='#ffa1b7'>[{}]</font><font color='#80ffe3'>[{}]</font>正在下载补丁：</b><br>".format(cusa_match.group(1),formatted_version))

            if appkgo and cusa_match and pkg and nojson and noDP and nopng:
                text = text.replace("GET", "<b><font color='#ffa1b7'>[{}]</font>正在下载本体：</b><br>".format(cusa_match.group(1)))

            if PPSA and pkg and nojson and noDP and nopng:
                text = text.replace("GET", "<b>正在下载PS5游戏：</b><br>")

            self.signal.emit(str(text))

    def flush(self):
        pass


#GUI
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        #self.setWindowIcon(QIcon("_ai.ico"))
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.dot_count = 0
        self.timer = QTimer()
        self.black_list = []
        self.client_connected = False
        #self.ui.tabWidget.setCurrentIndex(0)
        self.ui.ip_address.setText(get_local_ip())
        #self.ui.closeproxy.clicked.connect(self.stop_proxy)
        self.timer.timeout.connect(self.update_proxy_status)
        self.ui.proxy_switch.clicked.connect(self.start_proxy)
        self.ui.mode2.stateChanged.connect(self.handle_checkbox_state_change)
        self.ui.mode1.stateChanged.connect(self.handle_checkbox_state_change)
        self.ui.json_link_area.textChanged.connect(self.handle_json_link_area_text_change)

        #logs
        log_handler = LogHandler(self)
        log_handler.signal.connect(self.ui.logs.append)
        # 将LogHandler设置为Python的标准输出和标准错误流
        sys.stdout = log_handler
        sys.stderr = log_handler
        print(f"[{datetime.now().strftime('%m-%d %H:%M:%S')}] >> <font color='#fff'>RewindPS4 ver 0.5</font>")

    def set_label_text(self, label, text):
        font_metrics = QtGui.QFontMetrics(label.font())
        elided_text = font_metrics.elidedText(text, QtCore.Qt.ElideRight, label.width())
        label.setText(elided_text)
    
    def reset_game_info(self):
        self.ui.label_8.setText("待获取")
        self.ui.label_7.setText("待获取")
        self.ui.label_6.setText("待获取")

    def update_proxy_status(self):
        self.dot_count = (self.dot_count + 1) % 6  # 循环显示0到5个点
        self.ui.proxy_status.setText("代理服务器运行中" + "." * self.dot_count)

    def start_proxy(self):
        QMenu_style = '''
            QMenu {background:#353535;QMenu_stylecolor:#fff}
            QMenu::item:selected {background: #4a4a4a;color:cyan}
            '''
        if hasattr(self, 'proxy_thread') and self.proxy_thread.isRunning():
            self.stop_proxy()  
        else:
            json_link = self.ui.json_link_area.toPlainText().strip()
            if json_link == "" or json_link.endswith(".json") and json_link.startswith("http://gs2.ww.prod.dl.playstation.net/gs2/ppkgo/prod/"):
                self.proxy_thread = ProxyThread(self.ui, self.black_list)
                self.proxy_thread.start()
                self.setWindowTitle("RewindPS4 -运行中-")
                self.ui.proxy_switch.setText("终止代理")
                self.ui.proxy_status.setText("代理服务运行中")
                self.ui.proxy_status.setStyleSheet("color: cyan;font:800;border: 0")
                self.timer.start(200) 
                self.ui.mode1.setEnabled(False)
                self.ui.mode2.setEnabled(False)
                self.ui.json_link_area.setReadOnly(True) 
                self.ui.port.setReadOnly(True)
                self.ui.port.setStyleSheet(f'''
        QSpinBox {{background-color: #1E1E1E;color:#888}}
        {QMenu_style}  
        ''')

                self.ui.json_link_area.setStyleSheet(f'''
        QTextEdit {{background-color: #1E1E1E;color:#888}}
        {QMenu_style} 
        ''')
                self.ui.logs.setStyleSheet(f'''
        QTextEdit {{background-color: rgb(30, 30, 30);color: rgb(217, 217, 217);font: 9pt \"Arial\";border: 1px solid cyan}}
        {QMenu_style} 
        ''')
                self.ui.proxy_switch.setStyleSheet('''
        QPushButton {background-color: rgb(37,37,38); color: #fff;border: 1px solid cyan}
        QPushButton:hover {font:  11pt \"Microsoft YaHei UI\";border: 1px solid cyan}
                                        ''')

            else:
                msgBox = QMessageBox()
                msgBox.setStyleSheet("")
                msgBox.warning(self, "提示", "请输入正确补丁链接，或留空")

    def stop_proxy(self):
        QMenu_style = '''
            QMenu {background:#353535;QMenu_stylecolor:#fff}
            QMenu::item:selected {background:#4a4a4a;color:cyan}'''
        if hasattr(self, 'proxy_thread') and self.proxy_thread.isRunning():
            self.proxy_thread.terminate()
            self.proxy_thread.wait()
            self.setWindowTitle("RewindPS4")
            self.ui.proxy_switch.setText("启动代理")
            self.ui.proxy_status.setText("代理未启动")
            self.ui.proxy_status.setStyleSheet("color: #808080;border: 0")
            self.timer.stop()
            # 释放端口
            self.proxy_thread.server.socket.close()
            #self.ui.json_link_area.clear()
            self.black_list = []
            self.ui.mode1.setEnabled(True)
            self.ui.mode2.setEnabled(True)
            self.ui.json_link_area.setReadOnly(False) 
            self.ui.port.setReadOnly(False) 
            self.ui.json_link_area.setStyleSheet(f'''
        QTextEdit {{background-color: #1E1E1E;color:#fff}}
        QTextEdit:hover {{border: 1px solid cyan;}}
         {QMenu_style}
        ''')
            self.ui.port.setStyleSheet(f'''
        QSpinBox {{background-color: #1E1E1E;color:#fff}}
        QSpinBox:hover {{border: 1px solid cyan}}
         {QMenu_style}
        ''')

            self.ui.logs.setStyleSheet(f'''
        QTextEdit {{background-color: rgb(30, 30, 30);color: rgb(217, 217, 217);font: 9pt \"Arial\";border: 0}}
        {QMenu_style} 
        ''')           
            self.ui.proxy_switch.setStyleSheet('''
        QPushButton {background-color: rgb(37,37,38); color: #fff;border: 1px solid #fff}
        QPushButton:hover {font:  11pt \"Microsoft YaHei UI\";border: 1px solid cyan}
                                        ''')

            tprint("<br>🚨代理服务器已关闭")

    #关闭GUI，终止程序运行
    def closeEvent(self, event):
        if hasattr(self, 'proxy_thread') and self.proxy_thread.isRunning():
            self.proxy_thread.terminate()
            self.proxy_thread.wait()
        self.stop_proxy()  
        QtWidgets.QApplication.quit()
        os._exit(0)  
    

    def handle_checkbox_state_change(self, state):
        if self.sender() == self.ui.mode2:
            if state == QtCore.Qt.Checked:
                self.ui.mode1.setChecked(False)
                self.ui.json_link_area.clear()
                self.ui.json_link_area.setReadOnly(True)  
                self.reset_game_info()  
                self.black_list = ["gs-sec.ww.np.dl.playstation.net"]
            else:
                self.ui.json_link_area.setReadOnly(False)
                self.black_list = []
        elif self.sender() == self.ui.mode1:
            if state == QtCore.Qt.Checked:
                self.ui.mode2.setChecked(False)
                self.ui.json_link_area.setReadOnly(False)
                self.black_list = []
            else:

                self.black_list = ["gs-sec.ww.np.dl.playstation.net"]
                self.ui.json_link_area.clear()
                self.ui.json_link_area.setReadOnly(True)
                self.reset_game_info() 


    def handle_json_link_area_text_change(self):
        target_json = self.ui.json_link_area.toPlainText().strip()
        if not target_json:
            self.ui.json_input_status.setText("尚未输入连接")
            self.ui.json_input_status.setStyleSheet("color:#fff;border: 0")
            self.reset_game_info()
            self.ui.cover.hide()
        elif not (target_json.startswith("http://gs2.ww.prod.dl.playstation.net/gs2/ppkgo/prod/") and target_json.endswith(".json") and target_json.count(".json") == 1):
            self.ui.json_input_status.setText("请输入正确的补丁链接")
            self.reset_game_info()
            self.ui.cover.hide()

        else:
            self.target_json = target_json
            try:
                CUSA=extract_cusa_id(target_json)
                i = check_version(CUSA)
                self.set_label_text(self.ui.label_6, i[1])
                self.set_label_text(self.ui.label_7, i[0])
                self.ui.label_8.setText("<b><font color='#00ffff'>" + extract_version(target_json) + "</font></b>")
                self.ui.json_input_status.setText("已确定游戏版本")
                self.ui.json_input_status.setStyleSheet("border: 0;;color:#00c85a;font:10pt \"Microsoft YaHei UI Semibold\";")

                #显示游戏cover
                try:
                    j=title_metadata_info(CUSA)
                    cover_link=j[1]
                    self.ui.cover.image_url = cover_link  
                    response = requests.get(cover_link)
                    image = QtGui.QImage()
                    image.loadFromData(response.content)
                    pixmap = QPixmap(image)
                    scene = QGraphicsScene()
                    scene.addPixmap(pixmap)
                    self.ui.cover.setScene(scene)
                    self.ui.cover.show()
                    self.ui.cover.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
                except:
                    self.ui.cover.hide()

            except TypeError:
                self.ui.json_input_status.setText("获取版本失败，请检查网络")
                self.ui.json_input_status.setStyleSheet("color:#c80000;")
                self.ui.label_8.setText("获取失败")
                self.ui.label_7.setText("获取失败")
                self.ui.label_6.setText("获取失败")
                #self.reset_game_info() 

class ProxyThread(QtCore.QThread):
    def __init__(self, ui, black_list):
        super().__init__()
        self.ui = ui
        self.black_list = black_list
        self.server = None  # 初始化server

    def run(self):
        server_address = ('', self.ui.port.value())  # 设置服务器地址和端口
        target_json = self.ui.json_link_area.toPlainText().strip()# 获取用户输入的目标版本json链接
        ProxyHandler.target_json = target_json
        self.server = ThreadingHTTPServer(server_address, lambda *args, **kwargs: ProxyHandler(*args, black_list=self.black_list, **kwargs))  # 赋值server

        (host, port) = self.server.socket.getsockname()
        tprint(f"<br>✨代理服务器已启动<br>正在监听：{host}， 端口: {port}")
         # 在一个循环中运行代理服务器
        while QtWidgets.QApplication.instance():
            self.server.handle_request()
        self.ui.proxy_switch.setEnabled(True)



if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #自适应分辨率
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #使用高DPI位图
    app = QtWidgets.QApplication(sys.argv)
    app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough) #设置缩放因子的舍入策略
    font = QtGui.QFont("Arial", 9)
    app.setFont(font)
    window = MainWindow()
    window.setWindowIcon(QIcon('ico.ico'))
    window.show()
    sys.exit(app.exec_())