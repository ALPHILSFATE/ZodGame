import requests
import os
import re
from urllib.parse import urljoin

# 網站設定
BASE_URL = 'https://zodgame.xyz/'
LOGIN_URL = urljoin(BASE_URL, 'member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1')
SIGN_URL = urljoin(BASE_URL, 'plugin.php?id=dsu_paulsign:sign')

def login(session, username, password):
    # 先訪問首頁獲取必要的 cookie
    session.get(BASE_URL)
    
    # 執行登入
    login_data = {
        'fastloginfield': 'username',
        'username': username,
        'password': password,
        'quickforward': 'yes',
        'handlekey': 'ls'
    }
    
    response = session.post(LOGIN_URL, data=login_data)
    return 'succeedhandle_ls' in response.text

def sign(session):
    # 訪問簽到頁面
    response = session.get(SIGN_URL)
    
    # 獲取簽到表單數據
    formhash = re.search(r'name="formhash" value="([^"]+)"', response.text)
    if not formhash:
        raise Exception("無法獲取 formhash")
        
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
    
    if "簽到成功" in sign_response.text:
        return True
    elif "已經簽到" in sign_response.text:
        print("今天已經簽到過了")
        return True
    else:
        print(f"簽到失敗，回應內容：{sign_response.text}")
        return False

def main():
    username = os.environ.get('ZODGAME_USERNAME')
    password = os.environ.get('ZODGAME_PASSWORD')
    
    if not username or not password:
        raise Exception("請設定 ZODGAME_USERNAME 和 ZODGAME_PASSWORD 環境變數")
    
    session = requests.Session()
    
    # 設定請求標頭
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': BASE_URL,
        'Referer': SIGN_URL
    })
    
    try:
        if login(session, username, password):
            print("登入成功")
            if sign(session):
                print("簽到成功！")
            else:
                print("簽到失敗！")
                exit(1)
        else:
            print("登入失敗！")
            exit(1)
    except Exception as e:
        print(f"發生錯誤：{str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 