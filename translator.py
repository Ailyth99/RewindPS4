import json,locale



translation_json = """


{
"待获取": "Pending",
"游戏名称：": "GameName:",
"游戏编号：": "Game ID:",
"目标版本：": "Target Ver:",
"已http://gs2.ww开头，json结尾的补丁链接": "Patch link starting with http://gs2.ww and ending with .json",
"请粘贴目标补丁版本的json链接：": "Please paste the target patch version's json link:",
"模式1：下载指定版本": "Mode 1: Download Specified Version",
"目标游戏信息": "Target Game Info",
"尚未输入补丁链接": "No patch link entered yet",
"说明：模式2仅在PS4主机生效,": "Note: Mode 2 only works on PS4 console,",
"模式2：屏蔽补丁，只下载本体": "Mode 2: Block Patches, Base Game Only",
"本体一般情况下即版本号1.0的原始版本。": "Base game is usually the original version 1.0.",
"代理设置": "Proxy Settings",
"代理未启动": "Proxy Not Started",
"启动代理": "Start Proxy",
"本机IP：": "Local IP:",
"端口：": "Port:",
"运行日志": "Logs",
"前往获取补丁链接": "",
"详细使用指南": "Detailed Guide",
"快速指南": "Quick Guide",
"1.选择模式，模式1请填写目标版本json链接，\\n模式2直接勾选即可。": "1. Select mode, for Mode 1 enter target version json link,\\nfor Mode 2 just check the option.",
"2.点击启动代理，在主机网络设置的proxy\\n选项里面，填写好上面显示的IP或端口。\\n端口可自己指定。": "2. Click Start Proxy, in the proxy option\\nof console network settings, enter the IP and port\\nshown above. Port can be specified.",
"3.在主机上开始下载游戏。": "3. Start downloading the game on console.",
"获取CUSA编号失败，请检查补丁链接是否正确": "Failed to get CUSA ID, please check if patch link is correct",
"游戏ID错误": "Game ID Error",
"游戏ID错误或未提供":"Game ID Error or Blank",
"在PSN version XML中找不到版本号": "Cannot find version number in PSN version XML",
"无法连接更新服务器": "Unable to connect to update server",
"成功获取到游戏": "Successfully obtained game ",
"的基本信息": "'s basic info",
"从PSN服务器获取版本失败": "Failed to get version from PSN server",
"获取封面失败，但不影响锁定目标版本。": "Failed to obtain cover, but locking target version is not affected.",
"已屏蔽版本检查": "Version check blocked",
"找到最新版本:": "Found latest version:",
"错误：不属于同一个游戏ID<br>需要下载的游戏CUSA ID是": "Error: Not the same game ID<br>CUSA ID of game to download is ",
"替换的版本对应CUSA ID是": "CUSA ID you provided is ",
"PS5:报错CE-107893-8<br>PS4:直接报错无法下载": "PS5: Error CE-107893-8<br>PS4: Direct error cannot download",
"已映射版本为:": "Mapped version is:",
"链接被中断": "Connection interrupted",
"正在下载补丁：": "Downloading patch:",
"正在下载本体：": "Downloading base game:", 
"正在下载PS5游戏：": "Downloading PS5 game:",
"请确保PC和主机处于同一个网络中": "Please ensure PC and console are on the same network",
"代理服务器运行中": "Proxy server running",
"RewindPS4 -运行中-": "RewindPS4 - Running -",
"终止代理": "Stop Proxy",
"代理服务运行中": "Proxy service running",
"提示": "INFO",
"请输入正确补丁链接，或留空": "Please enter correct patch link, or blank",
"已被占用":"is already in use",
"代理未启动": "Proxy not started",
"代理服务器已关闭": "Proxy server has closed",
"尚未输入连接": "No link entered yet",
"请输入正确的补丁链接": "Please enter correct patch link",
"已确定游戏版本": "Game version determined",
"获取版本失败，请检查网络或json链接": "Failed to get version, check network or json link",
"获取失败": "Failed to get version",
"https://foggy-bath-a54.notion.site/RewindPS4-Guide-e130c168d2814ec288aad32d57518ed8?pvs=4":"https://foggy-bath-a54.notion.site/RewindPS4-Guide-ENGLISH-9ffe30e6e07a4077bc63b9c3511e458c?pvs=25",
"代理服务器已启动": "Proxy server started",
"端口已被占用，请更换端口（1024~65535）。":"Port is already in use. Please enter another port(1024-65535)",
"请将PS主机接入此代理服务器。": "Please connect your PS console to this proxy server.",
"PS4:网络设置→定制→proxy服务器→使用→填好IP和端口": "PS4: Network→Set up Internet Connection→LAN or Wifi→Custom→Proxy Server→Use→Enter IP Address and Port number",
"PS5:网络设置→选择某个网络→按Option→详细设置→proxy服务器开启→填写好IP和端口":"PS5:Network→Settings→Set up Internet Connection→Select your Network→Press Option button→Advanced Settings→Proxy Server→Use→Enter IP Address and port number"
}
"""


translations = json.loads(translation_json)
lang, _ = locale.getdefaultlocale()#获取系统语言

def tr(text):
    if lang == "zh_CN":
        return text
    
    return translations.get(text, text)

 