import requests
import os

# ===== 설정 =====
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

query = "펩소덴트"
store_name = "공감 클릭"

bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

# =================

def send_telegram(msg):

    # 🔴 확인 1: 토큰 확인
    if not bot_token:
        print("❌ bot_token이 없습니다.")
        return

    # 🔴 확인 2: chat_id 확인
    if not chat_id:
        print("❌ chat_id가 없습니다.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": msg
        }
    )

    # 🔴 확인 3: Telegram 응답 확인
    print("Telegram 상태:", response.status_code)
    print("Telegram 응답:", response.text)


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

    res = requests.get(
        url,
        headers=headers,
        params=params
    )

    print("네이버 상태:", res.status_code)

    items = res.json().get("items", [])

    print("검색 결과:", len(items))

    for item in items:

        title = item["title"]
        mall = item["mallName"]
        link = item["link"]

        print("상품:", title)
        print("판매처:", mall)

        # 🔴 여기 중요!
        if query in title and store_name in mall:

            msg = f"📢 상품 등록 발견!\n{title}\n{link}"

            send_telegram(msg)

            print("알림 전송:", title)


if __name__ == "__main__":
    check()
