from PyQt5 import QtCore, QtGui, QtWidgets
import requests

class MyGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(MyGraphicsView, self).__init__(parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.image_url = None  # 新增：用于保存图片的URL

    def showContextMenu(self, position):
        contextMenu = QtWidgets.QMenu(self)
        contextMenu.setStyleSheet('''
        QMenu {background-color: #353535; color: #fff}
        QMenu::item:selected {background-color: #4a4a4a;color:cyan}
        ''')
        saveAction = contextMenu.addAction("保存图片")
        saveAction.triggered.connect(self.saveImage)
        contextMenu.exec_(self.mapToGlobal(position))

    def saveImage(self):
        if self.image_url:
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "保存图片", "game_cover", "Images (*.png  *.jpg)")
            if fileName:
                response = requests.get(self.image_url)
                with open(fileName, 'wb') as f:
                    f.write(response.content)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1078, 557)
        Dialog.setStyleSheet("")
        self.groupBoxALL = QtWidgets.QGroupBox(Dialog)
        self.groupBoxALL.setGeometry(QtCore.QRect(0, -10, 1081, 571))
        self.groupBoxALL.setStyleSheet("background-color: rgb(42, 42, 42);")
        self.groupBoxALL.setObjectName("groupBoxALL")
        self.groupBoxALL.raise_()
        self.groupBox_version_setting = QtWidgets.QGroupBox(Dialog)
        self.groupBox_version_setting.setGeometry(QtCore.QRect(10, 10, 261, 541))
        self.groupBox_version_setting.setStyleSheet("color: rgb(249, 249, 249);\n"
"border: 1px solid rgb(63,63,70);")
        self.groupBox_version_setting.setTitle("")
        self.groupBox_version_setting.setObjectName("groupBox_version_setting")
        self.label_game_id = QtWidgets.QLabel(self.groupBox_version_setting)
        self.label_game_id.setGeometry(QtCore.QRect(24, 480, 53, 15))
        self.label_game_id.setStyleSheet("border: 0px ")
        self.label_game_id.setObjectName("label_game_id")
        self.label_7 = QtWidgets.QLabel(self.groupBox_version_setting)
        self.label_7.setGeometry(QtCore.QRect(80, 480, 101, 16))
        self.label_7.setStyleSheet("border: 0px ")
        self.label_7.setWordWrap(True)
        self.label_7.setObjectName("label_7")
        self.label_6 = QtWidgets.QLabel(self.groupBox_version_setting)
        self.label_6.setGeometry(QtCore.QRect(80, 456, 161, 16))
        self.label_6.setStyleSheet("border: 0px ")
        self.label_6.setWordWrap(True)
        self.label_6.setObjectName("label_6")
        self.label_game_name = QtWidgets.QLabel(self.groupBox_version_setting)
        self.label_game_name.setGeometry(QtCore.QRect(23, 456, 53, 15))
        self.label_game_name.setStyleSheet("border: 0px ")
        self.label_game_name.setObjectName("label_game_name")
        self.label_version = QtWidgets.QLabel(self.groupBox_version_setting)
        self.label_version.setGeometry(QtCore.QRect(23, 504, 53, 15))
        self.label_version.setStyleSheet("border: 0px ")
        self.label_version.setObjectName("label_version")
        self.label_8 = QtWidgets.QLabel(self.groupBox_version_setting)
        self.label_8.setGeometry(QtCore.QRect(80, 504, 61, 16))
        self.label_8.setStyleSheet("border: 0px ")
        self.label_8.setObjectName("label_8")
        self.label_4 = QtWidgets.QLabel(self.groupBox_version_setting)
        self.label_4.setGeometry(QtCore.QRect(21, 47, 181, 16))
        self.label_4.setStyleSheet("border: 0px ")
        self.label_4.setObjectName("label_4")
        self.mode1 = QtWidgets.QCheckBox(self.groupBox_version_setting)
        self.mode1.setGeometry(QtCore.QRect(20, 10, 211, 31))
        self.mode1.setToolTip("")
        self.mode1.setStatusTip("")
        self.mode1.setWhatsThis("")
        self.mode1.setAccessibleName("")
        self.mode1.setAccessibleDescription("")
        self.mode1.setStyleSheet("color: rgb(255, 255, 255);\n"
"font: 10pt \"Microsoft YaHei UI\";\n"
"border: 0px")
        self.mode1.setLocale(QtCore.QLocale(QtCore.QLocale.Chinese, QtCore.QLocale.China))
        self.mode1.setChecked(True)
        self.mode1.setObjectName("mode1")
        self.groupBox_3 = QtWidgets.QGroupBox(self.groupBox_version_setting)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 200, 241, 331))
        self.groupBox_3.setObjectName("groupBox_3")
        self.cover = MyGraphicsView(self.groupBox_3)
        self.cover.setGeometry(QtCore.QRect(10, 24, 221, 221))
        self.cover.setStyleSheet("background-color: rgb(42, 42, 42);border: 0")
        self.cover.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.cover.setObjectName("cover")
        self.json_link_area = QtWidgets.QTextEdit(self.groupBox_version_setting)
        self.json_link_area.setGeometry(QtCore.QRect(10, 70, 241, 101))
        self.json_link_area.setStyleSheet('''
        QTextEdit {background-color: rgb(30, 30, 30);color:#fff}
        QTextEdit:hover {border: 1px solid cyan;}
        QMenu {background:#353535;color:#fff}
        QMenu::item:selected {background: #4a4a4a;color:cyan}
        
        ''')
        self.json_link_area.setAcceptRichText(False)
        self.json_link_area.setObjectName("json_link_area")
        self.json_input_status = QtWidgets.QLabel(self.groupBox_version_setting)
        self.json_input_status.setGeometry(QtCore.QRect(10, 177, 141, 16))
        self.json_input_status.setStyleSheet("border: 0px ")
        self.json_input_status.setObjectName("json_input_status")
        self.groupBox_3.raise_()
        self.label_game_id.raise_()
        self.label_7.raise_()
        self.label_6.raise_()
        self.label_game_name.raise_()
        self.label_version.raise_()
        self.label_8.raise_()
        self.label_4.raise_()
        self.mode1.raise_()
        self.json_link_area.raise_()
        self.json_input_status.raise_()
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(280, 10, 271, 131))
        self.groupBox.setStyleSheet("color: rgb(244, 244, 244);border: 1px solid rgb(63,63,70);")
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.label_14 = QtWidgets.QLabel(self.groupBox)
        self.label_14.setGeometry(QtCore.QRect(20, 49, 231, 31))
        self.label_14.setToolTip("")
        self.label_14.setStyleSheet("border: 0")
        self.label_14.setObjectName("label_14")
        self.mode2 = QtWidgets.QCheckBox(self.groupBox)
        self.mode2.setGeometry(QtCore.QRect(20, 10, 211, 31))
        self.mode2.setToolTip("")
        self.mode2.setStatusTip("")
        self.mode2.setWhatsThis("")
        self.mode2.setAccessibleName("")
        self.mode2.setAccessibleDescription("")
        self.mode2.setStyleSheet("color: rgb(255, 255, 255);border: 0;\n"
"font: 10pt \"Microsoft YaHei UI\";")
        self.mode2.setLocale(QtCore.QLocale(QtCore.QLocale.Chinese, QtCore.QLocale.China))
        self.mode2.setChecked(False)
        self.mode2.setObjectName("mode2")
        self.label_15 = QtWidgets.QLabel(self.groupBox)
        self.label_15.setGeometry(QtCore.QRect(20, 80, 231, 31))
        self.label_15.setToolTip("")
        self.label_15.setStyleSheet("border: 0")
        self.label_15.setObjectName("label_15")
        self.groupBox_proxy_setting = QtWidgets.QGroupBox(Dialog)
        self.groupBox_proxy_setting.setGeometry(QtCore.QRect(280, 150, 271, 201))
        self.groupBox_proxy_setting.setStyleSheet("color: rgb(245, 245, 245);border: 1px solid rgb(63,63,70);")
        self.groupBox_proxy_setting.setObjectName("groupBox_proxy_setting")
        self.ip_address = QtWidgets.QLineEdit(self.groupBox_proxy_setting)
        self.ip_address.setGeometry(QtCore.QRect(90, 20, 141, 31))
        self.ip_address.setStyleSheet('''
        QLineEdit {background-color: rgb(37,37,38);background-color: rgb(30, 30, 30);}
        QMenu {background:#353535;color:#fff}
        QMenu::item:selected {background: #4a4a4a;color:cyan}
        ''')
        self.ip_address.setReadOnly(True)
        self.ip_address.setObjectName("ip_address")
        self.proxy_status = QtWidgets.QLabel(self.groupBox_proxy_setting)
        self.proxy_status.setGeometry(QtCore.QRect(80, 120, 131, 20))
        self.proxy_status.setStyleSheet("border: 0;")
        self.proxy_status.setAlignment(QtCore.Qt.AlignCenter)#文字居中
        self.proxy_status.setObjectName("proxy_status")
        self.proxy_switch = QtWidgets.QPushButton(self.groupBox_proxy_setting)
        self.proxy_switch.setGeometry(QtCore.QRect(50, 150, 181, 31))
        self.proxy_switch.setStyleSheet('''
        QPushButton {background-color: rgb(37,37,38); color: #fff;border: 1px solid #fff}
        QPushButton:hover {font:  11pt \"Microsoft YaHei UI\";border: 1px solid cyan}
                                        ''')
        self.proxy_switch.setObjectName("proxy_switch")
        self.port = QtWidgets.QSpinBox(self.groupBox_proxy_setting)
        self.port.setGeometry(QtCore.QRect(90, 70, 141, 31))
        self.port.setStyleSheet('''
        QSpinBox {background-color: rgb(30, 30, 30);}
        QSpinBox:hover {border: 1px solid cyan}
        QMenu{background:#353535;color:#fff}
        QMenu::item:selected {background: #4a4a4a;color:cyan}
''')
        self.port.setMaximum(65535)
        self.port.setProperty("value", 8080)
        self.port.setObjectName("port")
        self.label_ip = QtWidgets.QLabel(self.groupBox_proxy_setting)
        self.label_ip.setGeometry(QtCore.QRect(20, 30, 53, 15))
        self.label_ip.setStyleSheet("border: 0")
        self.label_ip.setObjectName("label_ip")
        self.label_port = QtWidgets.QLabel(self.groupBox_proxy_setting)
        self.label_port.setGeometry(QtCore.QRect(20, 80, 31, 16))
        self.label_port.setStyleSheet("border: 0")
        self.label_port.setObjectName("label_port")
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setGeometry(QtCore.QRect(560, 10, 511, 541))
        self.groupBox_2.setStyleSheet("color: rgb(255, 255, 255);border: 1px solid rgb(63,63,70);")
        self.groupBox_2.setObjectName("groupBox_2")
        self.logs = QtWidgets.QTextEdit(self.groupBox_2)
        self.logs.setGeometry(QtCore.QRect(10, 20, 491, 491))
        self.logs.setStyleSheet('''
        QTextEdit {background-color: rgb(30, 30, 30);color: rgb(217, 217, 217);font: 9pt \"Arial\";border: 0px}
        QMenu{background:#353535;color:#fff}
        QMenu::item:selected {background: #4a4a4a;color:cyan}
               ''')
        self.logs.setObjectName("logs")
        self.logs.setReadOnly(True)
        self.label_16 = QtWidgets.QLabel(self.groupBox_2)
        self.label_16.setGeometry(QtCore.QRect(280, 515, 231, 21))
        self.label_16.setToolTip("")
        self.label_16.setStyleSheet("border: 0")
        self.label_16.setObjectName("label_16")
        self.label_link = QtWidgets.QLabel(self.groupBox_2)
        self.label_link.setGeometry(QtCore.QRect(10, 518, 111, 16))
        self.label_link.setToolTip("")
        self.label_link.setStyleSheet('''
        QLabel {border: 0px;}
               ''')
        self.label_link.setObjectName("label_link")
        self.label_link.setOpenExternalLinks(True)
        self.groupBox_4 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_4.setGeometry(QtCore.QRect(280, 360, 271, 191))
        self.groupBox_4.setStyleSheet("color: rgb(244, 244, 244);border: 1px solid rgb(63,63,70);")
        self.groupBox_4.setObjectName("groupBox_4")
        self.label_10 = QtWidgets.QLabel(self.groupBox_4)
        self.label_10.setGeometry(QtCore.QRect(10, 16, 251, 51))
        self.label_10.setStyleSheet("border: 0")
        self.label_10.setObjectName("label_10")
        self.label_11 = QtWidgets.QLabel(self.groupBox_4)
        self.label_11.setGeometry(QtCore.QRect(10, 60, 251, 61))
        self.label_11.setStyleSheet("border: 0")
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(self.groupBox_4)
        self.label_12.setGeometry(QtCore.QRect(10, 120, 251, 31))
        self.label_12.setStyleSheet("border: 0")
        self.label_12.setObjectName("label_12")
        self.label_guide = QtWidgets.QLabel(self.groupBox_4)
        self.label_guide.setGeometry(QtCore.QRect(10, 160, 111, 16))
        self.label_guide.setStyleSheet("border: 0")
        self.label_guide.setObjectName("label_guide")
        self.label_guide.setOpenExternalLinks(True)
        self.groupBox_4.raise_()
        self.groupBox_2.raise_()
        self.groupBox_version_setting.raise_()
        self.groupBox.raise_()
        self.groupBox_proxy_setting.raise_()
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "RewindPS4"))
        self.label_game_id.setText(_translate("Dialog", "游戏编号："))
        self.label_7.setText(_translate("Dialog", "待获取"))
        self.label_6.setText(_translate("Dialog", "待获取"))
        self.label_game_name.setText(_translate("Dialog", "游戏名称："))
        self.label_version.setText(_translate("Dialog", "目标版本："))
        self.label_8.setText(_translate("Dialog", "待获取"))
        self.label_4.setToolTip(_translate("Dialog", "已http://gs2.ww开头，json结尾的补丁链接"))
        self.label_4.setText(_translate("Dialog", "请粘贴目标补丁版本的json链接："))
        self.mode1.setText(_translate("Dialog", "模式1：下载指定版本"))
        self.groupBox_3.setTitle(_translate("Dialog", "目标游戏信息"))
        self.json_input_status.setText(_translate("Dialog", "尚未输入补丁链接"))
        self.label_14.setText(_translate("Dialog", "说明：模式2仅在PS4主机生效,"))
        self.mode2.setText(_translate("Dialog", "模式2：屏蔽补丁，只下载本体"))
        self.label_15.setText(_translate("Dialog", "本体一般情况下即版本号1.0的原始版本。"))
        self.groupBox_proxy_setting.setTitle(_translate("Dialog", "代理设置"))
        self.ip_address.setPlaceholderText(_translate("Dialog", "255.255.255.255"))
        self.proxy_status.setText(_translate("Dialog", "代理未启动"))
        self.proxy_switch.setText(_translate("Dialog", "启动代理"))
        self.port.setToolTip(_translate("Dialog", "范围：1024~65535"))
        self.label_ip.setText(_translate("Dialog", "本机IP："))
        self.label_port.setText(_translate("Dialog", "端口："))
        self.groupBox_2.setTitle(_translate("Dialog", "运行日志"))
        self.label_16.setText(_translate("Dialog", "RewindPS4 V0.5 aikikarius@gmail.com"))
        self.label_link.setText(_translate("Dialog", "<a href='https://orbispatches.com/' style='color: #fff;'>前往获取补丁链接</a>"))
        self.label_guide.setText(_translate("Dialog", "<a href='https://foggy-bath-a54.notion.site/RewindPS4-Guide-e130c168d2814ec288aad32d57518ed8?pvs=4' style='color: #fff;'>详细使用指南</a>"))
        self.groupBox_4.setTitle(_translate("Dialog", "快速指南"))
        self.label_10.setText(_translate("Dialog", "1.选择模式，模式1请填写目标版本json链接，\n"
"模式2直接勾选即可。"))
        self.label_11.setText(_translate("Dialog", "2.点击启动代理，在主机网络设置的proxy\n"
"选项里面，填写好上面显示的IP或端口。\n"
"端口可自己指定。"))
        self.label_12.setText(_translate("Dialog", "3.在主机上开始下载游戏。"))
        self.groupBoxALL.setTitle(_translate("Dialog", "GroupBox"))
       