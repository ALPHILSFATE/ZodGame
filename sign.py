import requests
import os
import re
from urllib.parse import urljoin

# 網站設定
BASE_URL = 'https://zodgame.xyz/'
SIGN_URL = urljoin(BASE_URL, 'plugin.php?id=dsu_paulsign:sign')

def get_essential_cookies(cookie_str):
    """從完整的 cookie 字串中提取必要的 cookie"""
    essential_cookies = [
        'qhMq_2132_saltkey',
        'qhMq_2132_auth',
        'qhMq_2132_lastvisit',
        'qhMq_2132_ulastactivity'
    ]
    
    cookies = {}
    for item in cookie_str.split(';'):
        item = item.strip()
        if not item or '=' not in item:
            continue
        name, value = item.split('=', 1)
        name = name.strip()
        # 只保留必要的 cookie
        if name in essential_cookies:
            cookies[name] = value.strip()
    return cookies

def sign(session):
    try:
        # 訪問簽到頁面
        response = session.get(SIGN_URL)
        response.raise_for_status()
        
        # 檢查是否已登入
        if '您還未登錄' in response.text:
            print("Cookie 已過期或無效")
            return False
        
        # 檢查是否已經簽到
        if '您今天已經簽到過了' in response.text:
            print("今天已經簽到過了")
            return True
            
        # 獲取簽到表單數據
        formhash = re.search(r'name="formhash" value="([^"]+)"', response.text)
        if not formhash:
            print("無法獲取 formhash，可能未正確登入")
            return False
            
        # 執行簽到
        sign_data = {
            'formhash': formhash.group(1),
            'qdxq': 'kx',  # 心情：開心
            'qdmode': '1',  # 簽到模式
            'todaysay': '每日簽到',  # 簽到留言
            'fastreply': '0'
        }
        
        sign_url = f"{SIGN_URL}&operation=qiandao&infloat=1&inajax=1"
        sign_response = session.post(sign_url, data=sign_data)
        sign_response.raise_for_status()
        
        # 檢查回應內容中是否包含成功訊息
        if "恭喜你签到成功" in sign_response.text or "簽到成功" in sign_response.text:
            # 嘗試提取獎勵資訊
            reward_match = re.search(r'获得随机奖励\s*酱油\s*(\d+)\s*瓶', sign_response.text)
            if reward_match:
                print(f"簽到成功！獲得酱油 {reward_match.group(1)} 瓶")
            else:
                print("簽到成功！")
            return True
        elif "已經簽到" in sign_response.text or "已经签到" in sign_response.text:
            print("今天已經簽到過了")
            return True
        else:
            print(f"簽到失敗，回應內容：{sign_response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"網路請求錯誤：{str(e)}")
        return False
    except Exception as e:
        print(f"簽到過程發生錯誤：{str(e)}")
        return False

def main():
    # 從環境變數獲取 cookie
    cookie_str = os.environ.get('ZODGAME_COOKIE')
    if not cookie_str:
        raise Exception("請設定 ZODGAME_COOKIE 環境變數")
    
    # 建立 session 並設定 cookie
    session = requests.Session()
    session.cookies.update(get_essential_cookies(cookie_str))
    
    # 設定請求標頭
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': BASE_URL.rstrip('/'),
        'Referer': SIGN_URL
    })
    
    try:
        if sign(session):
            print("簽到操作完成")  # 修改提示訊息
            exit(0)  # 正常結束
        else:
            print("簽到失敗！")
            exit(1)
    except Exception as e:
        print(f"發生錯誤：{str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 