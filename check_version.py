# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 14:45:06 2023

@author: Sylph
"""
from datetime import datetime
import hmac,hashlib,binascii
import re,os,json,requests,socket,pathlib
import xml.etree.ElementTree as ET

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
        tprint('获取CUSA编号失败，请检查补丁链接是否正确')
    
    return str(match.group(1))


def check_version(cusa_id):
    if not re.match(r'CUSA\d{5}', cusa_id):
        print('游戏ID错误')

    try:  # 方法1
        key = binascii.unhexlify("AD62E37F905E06BC19593142281C112CEC0E7EC3E97EFDCAEFCDBAAFA6378D84")
        hash = hmac.new(key, ("np_" + cusa_id).encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        xml_url = f"https://gs-sec.ww.np.dl.playstation.net/plo/np/{cusa_id}/{hash}/{cusa_id}-ver.xml"

        response = requests.get(xml_url, verify=False)

        if response.status_code != 200:
            print(f'error ：gs-sec.ww.np.dl.playstation.net，CODE:{response.status_code}')
        else:
            XML=ET.fromstring(response.content)
            CUSA=XML.attrib["titleid"]
            title= XML.find(".//title").text
            version = XML.find(".//package").get("version")
           

            if version:
                #print("从xml获取成功")
                return CUSA,title,version.replace(".", "")
            else:
                print('在PSN version XML中找不到版本号')

    except Exception as e:
        print(f"无法检测更新<br>Failed to retrieve the latest version from the gs-sec.ww.np.dl.playstation.net: {e}")

    try:  # 方法2
        url = "https://huggingface.co/datasets/Ailyth/patch_info/raw/main/extracted_info.txt"
        response = requests.get(url,verify=False)
      
        if response.status_code == 200:
            game_list = response.text.split("\n")
            for game in game_list:
                if cusa_id in game:
                    version = game.split(",")[2]
                    #print("从hf获取到最新版本")

                    return version.replace(".", "")
            #print("在文本文件中找不到游戏信息")
        else:
            print(f"无法获取文本文件，CODE:{response.status_code}")

    except Exception as e:
        print(f"备份版本信息库获取失败<br>Failed to retrieve the backup version information database. You can try again several times, it may succeed: {e}")

    tprint("无法链接更新服务器,请检查本地网络是否能链接到gs-sec.ww.np.dl.playstation.net这个地址。")
    return None


def title_metadata_info(cusa_id):
    if not re.match(r'CUSA\d{5}', cusa_id):
        print('游戏ID错误')
    
    key_hex = "F5DE66D2680E255B2DF79E74F890EBF349262F618BCAE2A9ACCDEE5156CE8DF2CDF2D48C71173CDC2594465B87405D197CF1AED3B7E9671EEB56CA6753C2E6B0"
    game_id = (cusa_id + "_00").encode()  
    key = bytes.fromhex(key_hex)
    hmac_sha1 = hmac.new(key, game_id, hashlib.sha1)
    hash = hmac_sha1.hexdigest().upper()
    tmdb_json_url = f"http://tmdb.np.dl.playstation.net/tmdb2/{cusa_id}_00_{hash}/{cusa_id}_00.json"
    response = requests.get(tmdb_json_url)
    
    if response.status_code != 200:
        tprint(f'(本错误不会影响锁定版本)无法打开tmdb信息(CODE:{response.status_code})，该游戏没有tmdb信息')
    
    data = json.loads(response.text)
    #CUSA=data['npTitleId'].replace("_00", "")
    name = data['names'][0]['name']
    icon = data['icons'][0]['icon']
    tprint(f"成功获取到游戏《<font color='#a82fff'><b>{name}</b></font>》的基本信息")#{tmdb_json_url}<br>Get the title metadata of {name}：{tmdb_json_url}')
    
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



