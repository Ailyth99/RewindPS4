
from datetime import datetime
import hmac,hashlib,binascii
import re,os,json,requests,socket,pathlib
import xml.etree.ElementTree as ET
from translator import tr

def tprint(message):
    now = datetime.now().strftime('%m-%d %H:%M:%S')
    print(f"[{now}] >> {message}")

def is_valid_json_url(url):
    return url.startswith('http://gs2.ww.prod.dl.playstation.net/gs2/ppkgo/prod/') and url.endswith('.json')

def extract_cusa_id(url):
    if not url:
        return
    match = re.search(r'prod/(CUSA\d+)', url)
    if not match:
        tprint(tr('获取CUSA编号失败，请检查补丁链接是否正确'))
    
    return str(match.group(1))

i=True
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


def check_version(cusa_id):
    global i
    if not re.match(r'CUSA\d{5}', cusa_id):
        print(tr('游戏ID错误'))

    try:  # https://www.psdevwiki.com/ps4/Keys  https://gist.github.com/Zer0xFF/d94818f15e3e85b0b4d48000a4be1c73
        key = binascii.unhexlify("AD62E37F905E06BC19593142281C112CEC0E7EC3E97EFDCAEFCDBAAFA6378D84")
        hash = hmac.new(key, ("np_" + cusa_id).encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        xml_url = f"https://gs-sec.ww.np.dl.playstation.net/plo/np/{cusa_id}/{hash}/{cusa_id}-ver.xml"

        response = requests.get(xml_url, verify=False,headers=headers)

        if response.status_code != 200:
            tprint(f'error ：gs-sec.ww.np.dl.playstation.net，CODE:{response.status_code}')
        else:
            XML=ET.fromstring(response.content)
            CUSA=XML.attrib["titleid"]
            title= XML.find(".//title").text
            version = XML.find(".//package").get("version")
           

            if version:     
                if i:
                    tprint(f"{tr('成功获取到游戏')}<font color='#a82fff'><b><i>{title}</i></b></font>{tr('的基本信息')}")
                    i=False
                return CUSA,title,version.replace(".", ""),xml_url
            else:
                tprint(tr('在PSN version XML中找不到版本号'))

    except Exception as e:
        tprint(f"{tr('无法连接更新服务器')}<br>Failed to retrieve the latest version from the gs-sec.ww.np.dl.playstation.net: {e}")
    
    tprint(tr("从PSN服务器获取版本失败"))
    return None


def title_metadata_info(cusa_id):
    if not re.match(r'CUSA\d{5}', cusa_id):
        print(tr('游戏ID错误'))
    #https://www.psdevwiki.com/ps3/Keys
    key_hex = "F5DE66D2680E255B2DF79E74F890EBF349262F618BCAE2A9ACCDEE5156CE8DF2CDF2D48C71173CDC2594465B87405D197CF1AED3B7E9671EEB56CA6753C2E6B0"
    game_id = (cusa_id + "_00").encode()  
    key = bytes.fromhex(key_hex)
    hmac_sha1 = hmac.new(key, game_id, hashlib.sha1)
    hash = hmac_sha1.hexdigest().upper()
    #tmdb= Title Metadata DataBase
    tmdb_json_url = f"http://tmdb.np.dl.playstation.net/tmdb2/{cusa_id}_00_{hash}/{cusa_id}_00.json"
    response = requests.get(tmdb_json_url)
    
    if response.status_code != 200:
        tprint(f"{tr('获取封面失败，但不影响锁定目标版本。')}(CODE:{response.status_code})")
    
    data = json.loads(response.text)
    #CUSA=data['npTitleId'].replace("_00", "")
    name = data['names'][0]['name']
    icon = data['icons'][0]['icon']
    #tprint(f"成功获取到游戏《<font color='#a82fff'><b>{name}</b></font>》的基本信息")#{tmdb_json_url}<br>Get the title metadata of {name}：{tmdb_json_url}')
    
    return name, icon

def extract_version(url):
    pattern = r"-A(\d+)-"
    match = re.search(pattern, url)
    if match:
        version = match.group(1)
        formatted_version = f"{version[:2]}.{version[2:]}"
        return formatted_version
    else:
        return None

def get_local_ip():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        return local_ip
    except Exception as e:
        tprint(f"获取本机IP失败：{e}<br>Failed to get local IP: {e}")
        return "获取本机IP失败"



