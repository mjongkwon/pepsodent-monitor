import requests
import os

# ===== 설정 =====
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")

query = "펩소덴트"
store_name = "공감 클릭"

bot_token = os.getenv("bot_token")
chat_id = os.getenv("chat_id")

# =================

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(
        url,
        data={"chat_id": chat_id, "text": msg
             }
    )

def check():
    url = "https://openapi.naver.com/v1/search/shop.json"

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }

    params = {
        "query": query,
        "display": 10
    }

    res = requests.get(url, headers=headers, params=params)
    items = res.json().get("items", [])

    for item in items:
        title = item["title"]
        mall = item["mallName"]
        link = item["link"]

        if query in title and store_name in mall:
                msg = f"📢 상품 등록 발견!\n{title}\n{link}"
            
                send_telegram(msg)

                print("알림 전송:", title)

if __name__ == "__main__":
    check()
