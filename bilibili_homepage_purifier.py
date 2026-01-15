import requests
import hashlib
import time
import json
import re
import urllib.parse
import qrcode
import os
import sys
import platform
import subprocess
from urllib.parse import urlparse, parse_qs
import msvcrt
import traceback


# 配置文件路径
CONFIG_FILE = "config.json"

headers = {
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://space.bilibili.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://space.bilibili.com/',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
}


def wait_for_key_press():
    print("\n" + "="*50)
    print("按任意键继续...")
    
    try:
        # 如果是在Windows终端
        if platform.system() == "Windows":
            # 使用msvcrt.getch()等待按键
            msvcrt.getch()
        else:
            # 在其他系统上使用input()
            input()
    except Exception:
        # 如果出现异常，使用input()作为备用方案
        try:
            input()
        except Exception:
            pass


def exit_with_pause(code=0):
    wait_for_key_press()
    sys.exit(code)


def print_error_and_exit(error_msg, exit_code=1):
    print(f"\n❌ {error_msg}")
    exit_with_pause(exit_code)


def print_success_and_exit(success_msg, exit_code=0):
    print(f"\n✅ {success_msg}")
    exit_with_pause(exit_code)


# 配置文件管理类
class ConfigManager:
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.config = None
        
    def create_default_config(self):
        default_config = {
            "target_url": "https://live.bilibili.com/p/eden/area-tags?areaId=530&parentAreaId=1",
            "white_list": [
                "余生的客栈", "某二两", "吾昂王的模玩分享", "铃科SUZUKA", "剧经典回忆录", 
                "金艮君", "厂君助眠抽象助眠神", "冷水先森123", "春日部荣誉市民", "卡其ASMR",
                "巅峰拆卡", "蒙面人助眠", "QQ羊崽", "布谷max", "Fyzalk", "阿陈超级顶",
                "星界神起", "汪汪芝士椰", "哔哩哔哩会员购", "阿犬的日常asmr助眠",
                "小笙酱拆卡社", "瑾泽凌月", "赵清歌GEGE", "名创优品官方旗舰店", "凉niang",
                "小新动漫游戏迷-", "夜语闷声吃饱饱", "唱歌的雷子", "阿飞的周末",
                "杰尼龟校长教唱歌", "酒崽Pm9", "老铭MinGChunFun", "小J老师啊"
            ],
            "skip_sex": ["男"],
            "说明": {
                "target_url": "直播分区网址，必须包含areaId和parentAreaId参数",
                "white_list": "白名单用户名列表，这些用户不会被拉黑",
                "skip_sex": "跳过的性别列表，只能包含'男'、'女'、'保密'，这些性别的用户不会被拉黑",
                "重要提示": "请仔细填写配置文件，保存后按任意键继续"
            }
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)
            print(f"✅ 已创建默认配置文件: {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ 创建配置文件失败: {str(e)}")
            return False
    
    def open_config_file(self):
        try:
            if platform.system() == "Windows":
                os.startfile(self.config_file)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", self.config_file])
            else:  # Linux
                subprocess.call(["xdg-open", self.config_file])
            return True
        except Exception as e:
            print(f"❌ 无法自动打开配置文件: {str(e)}")
            print(f"请手动编辑文件: {os.path.abspath(self.config_file)}")
            return False
    
    def load_config(self):
        if not os.path.exists(self.config_file):
            print(f"❌ 配置文件不存在: {self.config_file}")
            print("正在创建默认配置文件...")
            if not self.create_default_config():
                return False
            
            print("\n" + "="*50)
            print("请编辑配置文件")
            print("="*50)
            print(f"配置文件已创建: {os.path.abspath(self.config_file)}")
            print("请按照以下说明填写:")
            print("1. target_url: 直播分区网址（必须包含areaId和parentAreaId参数）")
            print("2. white_list: 白名单用户名列表")
            print("3. skip_sex: 跳过的性别列表（只能包含'男'、'女'、'保密'）")
            
            if not self.open_config_file():
                print("\n请手动编辑配置文件，完成后按任意键继续...")
                wait_for_key_press()
            else:
                print("\n配置文件已打开，请编辑并保存，完成后按回车键继续...")
                wait_for_key_press()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"✅ 已加载配置文件: {self.config_file}")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件格式错误（JSON解析失败）: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ 加载配置文件失败: {str(e)}")
            return False
    
    def validate_config(self):
        if not self.config:
            print("❌ 配置为空，无法验证")
            return False
        
        errors = []
        
        # 验证target_url
        if "target_url" not in self.config:
            errors.append("缺少 'target_url' 字段")
        else:
            target_url = self.config["target_url"]
            try:
                query_params = parse_qs(urlparse(target_url).query)
                if 'areaId' not in query_params:
                    errors.append("target_url 中缺少 'areaId' 参数")
                if 'parentAreaId' not in query_params:
                    errors.append("target_url 中缺少 'parentAreaId' 参数")
            except Exception as e:
                errors.append(f"target_url 解析失败: {str(e)}")
        
        # 验证white_list
        if "white_list" not in self.config:
            errors.append("缺少 'white_list' 字段")
        elif not isinstance(self.config["white_list"], list):
            errors.append("'white_list' 必须是一个列表")
        
        # 验证skip_sex
        if "skip_sex" not in self.config:
            errors.append("缺少 'skip_sex' 字段")
        elif not isinstance(self.config["skip_sex"], list):
            errors.append("'skip_sex' 必须是一个列表")
        else:
            valid_sex = ["男", "女", "保密"]
            for sex in self.config["skip_sex"]:
                if sex not in valid_sex:
                    errors.append(f"无效的性别值: '{sex}'，只能是 {valid_sex}")
        
        if errors:
            print("\n❌ 配置文件验证失败，发现以下错误:")
            for error in errors:
                print(f"  - {error}")
            print(f"\n请修改配置文件 {self.config_file} 后重试")
            return False
        
        print("✅ 配置文件验证通过")
        return True
    
    def get_target_url(self):
        return self.config.get("target_url", "")
    
    def get_white_list(self):
        return self.config.get("white_list", [])
    
    def get_skip_sex(self):
        return self.config.get("skip_sex", [])
    
    def get_area_ids(self):
        target_url = self.get_target_url()
        try:
            query_params = parse_qs(urlparse(target_url).query)
            area_id = query_params.get('areaId', [''])[0]
            parent_area_id = query_params.get('parentAreaId', [''])[0]
            return area_id, parent_area_id
        except Exception as e:
            print(f"❌ 解析分区ID失败: {str(e)}")
            return "", ""
    
    def show_config_summary(self):
        if not self.config:
            return
        
        print("\n" + "="*50)
        print("配置摘要")
        print("="*50)
        print(f"分区URL: {self.get_target_url()}")
        
        area_id, parent_area_id = self.get_area_ids()
        print(f"子分区ID: {area_id}")
        print(f"父分区ID: {parent_area_id}")
        
        white_list = self.get_white_list()
        print(f"白名单用户数: {len(white_list)}")
        if white_list:
            print(f"白名单前5个: {', '.join(white_list[:5])}{'...' if len(white_list) > 5 else ''}")
        
        skip_sex = self.get_skip_sex()
        print(f"跳过的性别: {', '.join(skip_sex)}")
        print("="*50)

# 登录系统类
class BilibiliQRLogin:
    def __init__(self):
        self.session = requests.Session()
        self.cookies = {}
        
        # 设置基础headers
        self.headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://www.bilibili.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.bilibili.com/',
            'sec-ch-ua': '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0',
        }
        
        self.session.headers.update(self.headers)
        
    def get_initial_cookies(self):
        # 访问B站主页获取初始cookies
        try:
            response = self.session.get(
                'https://www.bilibili.com',
                timeout=10
            )
            
            if response.status_code == 200:
                # 获取response中的cookies
                self.cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
                return True
            else:
                return False
                
        except Exception as e:
            return False
            
    def get_qrcode(self):
        print("正在获取登录二维码...")
        
        # 如果还没有初始cookies，先获取
        if not self.cookies:
            if not self.get_initial_cookies():
                return None, None
        
        # 设置二维码请求的特殊headers
        qr_headers = {
            **self.headers,
            'accept': 'application/json, text/plain, */*',
            'origin': 'https://passport.bilibili.com',
            'referer': 'https://passport.bilibili.com/login?from_spm_id=333.337.0.0',
        }
        
        try:
            response = self.session.get(
                'https://passport.bilibili.com/x/passport-login/web/qrcode/generate',
                headers=qr_headers,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"获取二维码失败，状态码: {response.status_code}")
                return None, None
                
            qrcode_data = response.json()
            
            if qrcode_data.get('code') != 0:
                print(f"获取二维码失败: {qrcode_data.get('message', '未知错误')}")
                return None, None
                
            qrcode_url = qrcode_data['data']['url']
            qrcode_key = qrcode_data['data']['qrcode_key']
            
            return qrcode_url, qrcode_key
            
        except Exception as e:
            print(f"❌ 获取二维码出错: {str(e)}")
            return None, None
            
    def display_qrcode(self, url):
        print("\n" + "="*50)
        print("请使用Bilibili APP扫描以下二维码:")
        print("="*50)
        
        # 尝试生成ASCII二维码
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=2,
                border=1,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # 生成ASCII二维码
            qr.print_ascii(invert=True)
        except Exception as e:
            print(f"生成ASCII二维码失败: {str(e)}")
            print(f"请直接使用以下URL: {url}")
        
        
    def poll_login_status(self, qrcode_key, timeout=180):
        print("等待扫码登录...")
        start_time = time.time()
        
        # 设置轮询的特殊headers
        poll_headers = {
            **self.headers,
            'accept': 'application/json, text/plain, */*',
            'origin': 'https://passport.bilibili.com',
            'referer': 'https://passport.bilibili.com/login?from_spm_id=333.337.0.0',
        }
        
        while time.time() - start_time < timeout:
            try:
                response = self.session.get(
                    f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={qrcode_key}',
                    headers=poll_headers,
                    timeout=10
                )
                
                if response.status_code != 200:
                    print(f"轮询失败，状态码: {response.status_code}")
                    time.sleep(2)
                    continue
                    
                login_data = response.json()
                
                code = login_data['data']['code']
                message = login_data['data'].get('message', '')
                
                if code == 0:
                    # 登录成功
                    login_url = login_data['data']['url']
                    print("✅ 登录成功！")
                    return login_url
                elif code == 86038:
                    # 二维码已失效
                    print("❌ 二维码已失效，请重新获取")
                    return None
                else:
                    pass
                    
                time.sleep(2)
                
            except Exception as e:
                time.sleep(2)
                
        print("⏰ 登录超时")
        return None
        
    def extract_cookies_from_url(self, login_url):
        try:
            # 解析URL参数
            parsed_url = urllib.parse.urlparse(login_url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            cookies = {}
            
            # 提取关键cookies
            if 'DedeUserID' in query_params:
                cookies['DedeUserID'] = query_params['DedeUserID'][0]
                
            if 'DedeUserID__ckMd5' in query_params:
                cookies['DedeUserID__ckMd5'] = query_params['DedeUserID__ckMd5'][0]
                
            if 'SESSDATA' in query_params:
                cookies['SESSDATA'] = query_params['SESSDATA'][0]
                
            if 'bili_jct' in query_params:
                cookies['bili_jct'] = query_params['bili_jct'][0]
                
            if 'Expires' in query_params:
                cookies['Expires'] = query_params['Expires'][0]
                
            return cookies
            
        except Exception as e:
            print(f"❌ 解析登录URL出错: {str(e)}")
            return {}
            
    def update_session_cookies(self, new_cookies):
        # 更新session的cookies
        for name, value in new_cookies.items():
            self.session.cookies.set(name, value)
        
        # 更新类的cookies字典
        self.cookies.update(new_cookies)
        return self.cookies
        
    def verify_cookies(self):
        try:
            response = self.session.get(
                'https://api.bilibili.com/x/web-interface/nav',
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('code') == 0:
                    user_info = data.get('data', {})
                    return True
                else:
                    print(f"❌ Cookies无效，错误码: {data.get('code')}")
                    return False
            else:
                print(f"❌ 验证请求失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 验证过程中出错: {str(e)}")
            return False
            
    def login(self):
        # 1. 获取初始cookies
        if not self.get_initial_cookies():
            print("❌ 获取初始cookies失败")
            return False
            
        # 2. 获取二维码
        qrcode_url, qrcode_key = self.get_qrcode()
        if not qrcode_url or not qrcode_key:
            print("❌ 获取二维码失败")
            return False
            
        # 3. 显示二维码
        self.display_qrcode(qrcode_url)
        
        # 4. 轮询登录状态
        login_url = self.poll_login_status(qrcode_key)
        if not login_url:
            return False
            
        # 5. 提取cookies
        new_cookies = self.extract_cookies_from_url(login_url)
        if not new_cookies:
            print("❌ 无法从登录URL中提取cookies")
            return False
            
        # 6. 更新cookies
        self.update_session_cookies(new_cookies)
        
        # 7. 验证cookies
        if self.verify_cookies():
            print("\n🎉 登录成功！")
            
            # 保存cookies到文件
            self.save_cookies()
            return True
        else:
            print("\n❌ 登录失败")
            return False
            
    def save_cookies(self, filename='bilibili_cookies.json'):
        try:
            # 将RequestsCookieJar转换为字典
            cookies_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(cookies_dict, f, indent=2, ensure_ascii=False)
            print(f"✅ Cookies已保存到: {filename}")
            return True
        except Exception as e:
            print(f"❌ 保存cookies失败: {str(e)}")
            return False
            
    def load_cookies(self, filename='bilibili_cookies.json'):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                cookies_dict = json.load(f)
                
            # 清空当前session的cookies
            self.session.cookies.clear()
            
            # 加载cookies到session
            for name, value in cookies_dict.items():
                self.session.cookies.set(name, value)
                
            self.cookies = cookies_dict
            print(f"✅ 已从 {filename} 加载cookies")
            return True
        except FileNotFoundError:
            print(f"❌ 文件 {filename} 不存在")
            return False
        except Exception as e:
            print(f"❌ 加载cookies失败: {str(e)}")
            return False
            
    def get_user_info(self):
        try:
            response = self.session.get(
                'https://api.bilibili.com/x/space/myinfo',
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    return data.get('data', {})
        except Exception as e:
            print(f"获取用户信息失败: {str(e)}")
        return {}
        
    def get_cookies_dict(self):
        return requests.utils.dict_from_cookiejar(self.session.cookies)
    
    def run_login_flow(self):
        print("\n" + "="*50)
        print("B站自动拉黑脚本 - 登录系统")
        print("="*50)
        
        # 尝试加载已有cookies
        print("\n尝试加载已有cookies...")
        if self.load_cookies():
            if self.verify_cookies():
                print("✅ 已有cookies有效，无需重新登录")
                
                # 显示用户信息
                user_info = self.get_user_info()
                if user_info:
                    print(f"\n用户信息:")
                    print(f"  昵称: {user_info.get('name', '未知')}")
                    print(f"  等级: {user_info.get('level', '未知')}")
                    print(f"  硬币: {user_info.get('coins', 0)}")
                    print(f"  粉丝数: {user_info.get('follower', 0)}")
                    
                return True
            else:
                print("❌ 已有cookies无效，需要重新登录")
        else:
            print("❌ 未找到cookies文件，需要登录")
            
        # 开始登录流程
        print("\n开始新的登录流程...")
        if self.login():
            print("\n✅ 登录成功！")
            return True
        else:
            print("\n❌ 登录失败，请重试")
            return False

def get_wbi_keys(cookies):
    print("[自动拉黑]正在获取wbi密钥...")
    nav_url = "https://api.bilibili.com/x/web-interface/nav"
    
    try:
        response = requests.get(nav_url, cookies=cookies, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0 and "data" in data and "wbi_img" in data["data"]:
                wbi_img = data["data"]["wbi_img"]
                img_url = wbi_img["img_url"]
                sub_url = wbi_img["sub_url"]
                
                # 从URL中提取密钥
                img_key = img_url.split("/")[-1].split(".")[0]
                sub_key = sub_url.split("/")[-1].split(".")[0]
                
                print(f"[自动拉黑]成功获取wbi密钥:")
                return img_key, sub_key
    except Exception as e:
        print(f"[自动拉黑]获取wbi密钥失败: {e}")
    
    # 如果获取失败，使用固定密钥
    print("[自动拉黑]使用内置固定密钥")
    return None, None

def generate_mix_key(img_key, sub_key):
    if not img_key or not sub_key:
        # 如果密钥获取失败，使用固定mixKey
        return "ea1db124af3c7062474693fa704f4ff8"
    
    combined = img_key + sub_key
    # JS代码中的重排索引
    indices = [46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52]
    
    chars = []
    for idx in indices:
        if idx < len(combined):
            chars.append(combined[idx])
    
    return "".join(chars)[:32]

def generate_wrid(params, img_key=None, sub_key=None):
    # 生成混合密钥
    mix_key = generate_mix_key(img_key, sub_key)
    
    # 1. 按键名排序
    sorted_keys = sorted(params.keys())
    
    # 2. 构建查询字符串
    encoded_params = []
    for key in sorted_keys:
        value = str(params[key])
        value = value.replace("!", "").replace("'", "").replace("(", "").replace(")", "").replace("*", "")
        encoded_params.append(f"{urllib.parse.quote(key)}={urllib.parse.quote(value)}")
    
    query_string = "&".join(encoded_params)
    
    # 3. 拼接混合密钥并计算MD5
    string_to_hash = query_string + mix_key
    return hashlib.md5(string_to_hash.encode()).hexdigest()

def get_webid(cookies, area_id, parent_area_id):
    print("[自动拉黑]正在获取新的webid")
    try:
        page = requests.get(f"https://live.bilibili.com/p/eden/area-tags?areaId={area_id}&parentAreaId={parent_area_id}", cookies=cookies, headers=headers)
        pattern = r'<script>window\._render_data_\s*=\s*({.*?access_id":.*?})'
        match = re.search(pattern, page.text, re.DOTALL)
        if match:
            render_data_json = match.group(1)
            w_webid = json.loads(render_data_json)['access_id']
            print("[自动拉黑]webid获取成功！")
            return w_webid
    except Exception as e:
        print(f"[自动拉黑]webid获取失败: {e}")
    
    # 如果获取失败，使用内置webid
    print("[自动拉黑]webid获取失败，启用内置webid")
    return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzcG1faWQiOiI0NDQuMjUzIiwiYnV2aWQiOiJDODE2RkUxQi0zMUI0LTlEMEQtNkY2RC1BODVCOUVCMzUzNjExMDA5NWluZm9jIiwidXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS8xMzcuMC4wLjAgU2FmYXJpLzUzNy4zNiBFZGcvMTM3LjAuMC4wIiwiY3JlYXRlZF9hdCI6MTc0OTYyMDIwMSwidHRsIjo4NjQwMCwidXJsIjoibGl2ZS5iaWxpYmlsaS5jb20vcC9lZGVuL2FyZWEtdGFncz9wYXJlbnRBcmVhSWQ9MVx1MDAyNmFyZWFJZD01MzAiLCJyZXN1bHQiOiJub3JtYWwiLCJpc3MiOiJnYWlhIiwiaWF0IjoxNzQ5NjIwMjAxfQ.jNKl9WWVib53bakj24xtE_ggzt2nOJ91dAjoui7m0UWY1R4md3MfammDuf8qWnrrimKTdkPc5e840KGERBBWhxuBZFtBw8fsURRG8a3InefmSay4rOTbn498hZGpxXNeZMVBME6MsXi25U2LN5ILkBYnKmmqp2UBMFJuAthocNdoQGGkupezudUbRtkqdDx3-52Yy-JBOYoThGuIu-D4-tzkb-En7aVu1x6Fx2JuOvmmFW7-q6RJ9ssRfyGBkuvCuaF6YanI7D-FQJ_gsb7atemhsqoCNvpt9HMEzUXoTtrgOU-2FaMtT7ENY12x0VFhyPu3k8vuVFjXxMbGE1_EkQ"

def get_user_gender(mid, img_key=None, sub_key=None, cookies=None):
    try:
        # 构建参数
        params = {
            'mid': mid,
            'token': '',
            'platform': 'web',
            'web_location': '1550101',
            'wts': str(int(time.time())),
        }
        
        # 生成w_rid
        w_rid = generate_wrid(params, img_key, sub_key)
        
        # 添加w_rid到参数
        params['w_rid'] = w_rid
        
        # 发送请求
        url = 'https://api.bilibili.com/x/space/wbi/acc/info'
        response = requests.get(url, params=params, cookies=cookies, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0 and 'data' in data:
                return data['data'].get('sex', '未知')
            else:
                print(f"[自动拉黑]获取用户 {mid} 信息失败: {data.get('message', '未知错误')}")
                return '未知'
        else:
            print(f"[自动拉黑]请求用户信息失败，状态码: {response.status_code}")
            return '未知'
            
    except Exception as e:
        print(f"[自动拉黑]获取用户性别时出错: {e}")
        return '未知'

def blacklist_user(uid, name, cookies):
    data = 'fid='+str(uid)+'&act=5&re_src=11&gaia_source=web_main&spmid=333.1387.0.0&extend_content=%7B%22entity%22:%22user%22,%22entity_id%22:'+str(uid)+'%7D&csrf='+ cookies.get('bili_jct', '')
    black_res = requests.post(
        'https://api.bilibili.com/x/relation/modify?statistics=%7B%22appId%22:100,%22platform%22:5%7D',
        cookies=cookies,
        headers=headers,
        data=data,
    )
    
    return black_res.json()

# 主程序
if __name__ == "__main__":
    try:
        print("="*50)
        print("B站主页净化助手 - 自动化拉黑工具")
        print("="*50)
        
        # 1. 初始化配置管理器
        config_manager = ConfigManager()
        
        # 2. 加载并验证配置
        print("\n加载配置文件...")
        if not config_manager.load_config():
            print_error_and_exit("加载配置文件失败，程序退出", 1)
        
        if not config_manager.validate_config():
            print_error_and_exit("配置文件验证失败，程序退出", 1)
        
        # 显示配置摘要
        config_manager.show_config_summary()
        
        # 3. 初始化登录系统
        login_system = BilibiliQRLogin()
        
        # 4. 运行登录流程
        if not login_system.run_login_flow():
            print_error_and_exit("登录失败，程序退出", 1)
        
        # 5. 获取cookies字典
        cookies = login_system.get_cookies_dict()
        
        # 6. 从配置中获取参数
        target_url = config_manager.get_target_url()
        white_list = config_manager.get_white_list()
        skip_sex = config_manager.get_skip_sex()
        AREA_ID, PARENT_AREA_ID = config_manager.get_area_ids()
        
        print("\n" + "="*50)
        print("开始自动拉黑任务")
        print("="*50)
        
        # 7. 获取wbi密钥
        img_key, sub_key = get_wbi_keys(cookies)
        
        # 8. 获取webid
        w_webid = get_webid(cookies, AREA_ID, PARENT_AREA_ID)
        
        # 统计变量
        blacklist_count = 0
        already_blacklisted_count = 0
        white_list_skipped_count = 0
        male_skipped_count = 0
        login_error = False
        
        for n in range(1, 100):
            print("="*50)
            wts = round(time.time())
            print(f'[自动拉黑]正在抓取第 {n} 页，当前时间 {wts}')
            
            # 构建参数
            params = {
                'platform': 'web',
                'parent_area_id': str(PARENT_AREA_ID),
                'area_id': str(AREA_ID),
                'sort_type': '',
                'page': str(n),
                'vajra_business_key': '',
                'web_location': '444.253',
                'w_webid': w_webid,
                'wts': str(wts),
            }
            
            # 生成w_rid
            w_rid = generate_wrid(params, img_key, sub_key)
            
            # 将w_rid添加到参数中
            params['w_rid'] = w_rid
            
            print("="*50)
            
            # 直播列表的链接
            list_url = 'https://api.live.bilibili.com/xlive/web-interface/v1/second/getList'
            
            # 发送请求获取直播列表
            response = requests.get(
                list_url,
                params=params,
                cookies=cookies,
                headers=headers,
            )
            
            main = json.loads(response.text)
            
            if main['code'] == 0:
                live_list = main['data']['list']
                if len(live_list) < 1:
                    print("[自动拉黑]工作完毕！下班收工！")
                    break
                
                for i in range(len(live_list)):
                    name = live_list[i]['uname']
                    uid = str(live_list[i]['uid'])

                    # 检查是否在白名单中
                    if name in white_list:
                        print(f"[自动拉黑]检测到白名单目标 {name}，已跳过")
                        white_list_skipped_count += 1
                        continue
                    
                    # 获取用户性别
                    print(f"[自动拉黑]正在获取用户 {uid} - {name} 的性别信息...")
                    if len(skip_sex) == 0:
                        result = blacklist_user(uid, name, cookies)
                    elif len(skip_sex)>0 and len(skip_sex)<3:
                        gender = get_user_gender(uid, img_key, sub_key, cookies)
                        
                        # 检查性别
                        if gender in skip_sex:
                            print(f"[自动拉黑]用户 {uid} - {name} 性别为{gender}，跳过拉黑")
                            male_skipped_count += 1
                            
                            # 添加短暂延迟，避免请求过快
                            time.sleep(0.2)
                            continue

                        result = blacklist_user(uid, name, cookies)
                    else:
                        print(f"[自动拉黑]用户 {uid} - {name} 性别为{gender}，跳过拉黑")
                        continue
                    
                    if result['code'] == 0:
                        print(f"[自动拉黑]用户 {name} (性别: {gender}) 拉黑成功")
                        blacklist_count += 1
                    elif result['code'] == 22120:
                        print(f"[自动拉黑]用户 {name} (性别: {gender}) 已经被拉黑")
                        already_blacklisted_count += 1
                    elif result['code'] == -101:
                        print(f"[自动拉黑]账号未登录！请检查cookies")
                        login_error = True
                        break
                    else:
                        print(f"[自动拉黑]拉黑失败: {result}")
                    
                    # 添加短暂延迟，避免请求过快
                    time.sleep(0.2)
                
                if login_error:
                    break
                
                # 添加延迟，避免请求过快
                time.sleep(0.5)
                
            else:
                print('[自动拉黑]请求出错:', response.text)
                break

        # 输出统计信息
        print("\n" + "="*50)
        print("[自动拉黑]任务完成！")
        print(f"白名单跳过: {white_list_skipped_count} 个用户")
        print(f"性别跳过: {male_skipped_count} 个用户")
        print(f"成功拉黑: {blacklist_count} 个用户")
        print(f"已拉黑用户: {already_blacklisted_count} 个用户")
        print("="*50)
        
        # 正常退出
        print_success_and_exit("程序执行完成", 0)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断程序执行")
        exit_with_pause(0)
    except Exception as e:
        print("\n❌ 程序发生未预期的错误:")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print("\n错误详情:")
        traceback.print_exc()
        exit_with_pause(1)
