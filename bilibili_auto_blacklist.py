import requests
import hashlib
import time
import json
import re
import urllib.parse
from urllib.parse import urlparse, parse_qs


# 分区配置 - 在这里填写分区网址
# 默认为萌宅领域分区
target_url = 'https://live.bilibili.com/p/eden/area-tags?areaId=530&parentAreaId=1'

# 这里粘贴你的B站cookies
cookies = {
}

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

# 白名单列表，建议自己修改
white_list = ['余生的客栈', '某二两', '吾昂王的模玩分享', '铃科SUZUKA', '剧经典回忆录', '金艮君', '厂君助眠抽象助眠神',
              '冷水先森123', '春日部荣誉市民', '卡其ASMR', '巅峰拆卡', '蒙面人助眠', 'QQ羊崽', '布谷max', 'Fyzalk',
              '阿陈超级顶', '星界神起', '汪汪芝士椰', '哔哩哔哩会员购', '阿犬的日常asmr助眠', '小笙酱拆卡社', '瑾泽凌月',
              '赵清歌GEGE', '名创优品官方旗舰店', '凉niang', '小新动漫游戏迷-', '夜语闷声吃饱饱', '唱歌的雷子', '阿飞的周末',
              '杰尼龟校长教唱歌', '酒崽Pm9', '老铭MinGChunFun', '小J老师啊']

# 性别判断拉黑逻辑，最简单的擦边账号判断方法
# 只能为“男”“女”“保密”，列表中性别将跳过拉黑
skip_sex = ['男']

# 从URL解析分区ID
AREA_ID = parse_qs(urlparse(target_url).query).get('areaId', [''])[0]
PARENT_AREA_ID = parse_qs(urlparse(target_url).query).get('parentAreaId', [''])[0]

def get_wbi_keys():
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
                print(f"  img_key: {img_key}")
                print(f"  sub_key: {sub_key}")
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

def get_webid():
    print("[自动拉黑]正在获取新的webid")
    try:
        page = requests.get(f"https://live.bilibili.com/p/eden/area-tags?areaId={AREA_ID}&parentAreaId={PARENT_AREA_ID}", cookies=cookies, headers=headers)
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

def get_user_gender(mid, img_key=None, sub_key=None):
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

def blacklist_user(uid, name):
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
    # 获取wbi密钥
    img_key, sub_key = get_wbi_keys()
    
    # 获取webid
    w_webid = get_webid()
    
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
        print(f"[自动拉黑]新的w_rid为: {w_rid}")
        
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
                print("[自动拉黑]爬取完毕！下班收工！")
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
                gender = get_user_gender(uid, img_key, sub_key)
                
                # 检查性别
                if gender in skip_sex:
                    print(f"[自动拉黑]用户 {uid} - {name} 性别为{gender}，跳过拉黑")
                    male_skipped_count += 1
                    
                    # 添加短暂延迟，避免请求过快
                    time.sleep(0.2)
                    continue
                
                # 拉黑用户
                result = blacklist_user(uid, name)
                
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
    print(f"成功拉黑: {blacklist_count} 个用户")
    print(f"已拉黑用户: {already_blacklisted_count} 个用户")
    print("="*50)
