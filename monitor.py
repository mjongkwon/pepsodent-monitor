import requests
import json
import os

# ===== 설정 =====
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

query = "펩소덴트"
store_name = "공감 클릭"

bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

data_file = "sent_items.json"
# =================

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

def load_sent():
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            return json.load(f)
    return []

def save_sent(data):
    with open(data_file, "w") as f:
        json.dump(data, f)

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

    print("HTTP 상태:", res.status_code)
    print("응답 내용:", res.text[:3000])

    res.raise_for_status()

    items = res.json().get("items", [])

    print("검색 결과 개수:", len(items))

    sent_list = load_sent()

    for item in items:
        title = item["title"]
        mall = item["mallName"]
        link = item["link"]

        print("상품:", title)
        print("판매몰:", mall)

        key = title + mall

        if query in title and store_name in mall:
            print("조건 일치!")

            if key not in sent_list:
                msg = f"📢 상품 등록 발견!\n{title}\n{link}"
                send_telegram(msg)

                sent_list.append(key)
                save_sent(sent_list)

                print("알림 전송:", title)
            else:
                print("이미 알림 보냄:", title)
        else:
            print("조건 불일치")

if __name__ == "__main__":
    check()
