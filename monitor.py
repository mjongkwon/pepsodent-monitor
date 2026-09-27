import requests
import os

# ===== 설정 =====

# 🔴 수정/확인 1
# GitHub Secrets에 등록한 이름과 정확히 같아야 합니다.
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")

query = "펩소덴트"
store_name = "공감 클릭"

# 🔴 수정/확인 2
# GitHub Secrets에 아래 이름으로 등록되어 있어야 합니다.
# bot_token
# chat_id
bot_token = os.getenv("bot_token")
chat_id = os.getenv("chat_id")

# =================


def send_telegram(msg):

    # 🔴 수정/확인 3
    # bot_token이 제대로 들어왔는지 확인
    if not bot_token:
        print("❌ bot_token이 없습니다.")
        return

    # 🔴 수정/확인 4
    # chat_id가 제대로 들어왔는지 확인
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

    # 🔴 수정/확인 5
    # Telegram이 정상적으로 메시지를 보냈는지 확인
    print("Telegram 응답:", response.status_code)
    print("Telegram 내용:", response.text)

    # 성공 여부 확인
    if response.status_code == 200:
        print("✅ 텔레그램 전송 성공")
    else:
        print("❌ 텔레그램 전송 실패")


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

    # 🔴 수정/확인 6
    # 네이버 API가 정상적으로 응답하는지 확인
    print("네이버 응답:", res.status_code)
    print("네이버 결과:", res.text[:500])

    items = res.json().get("items", [])

    print("검색 결과 개수:", len(items))

    for item in items:

        title = item["title"]
        mall = item["mallName"]
        link = item["link"]

        print("상품:", title)
        print("판매처:", mall)

        # 🔴 수정/확인 7
        # 현재 조건이 너무 정확하게 맞아야 합니다.
        # title에 '펩소덴트'가 있고
        # mallName에 '공감 클릭'이 있어야만 텔레그램이 갑니다.
        if query in title and store_name in mall:

            msg = f"📢 상품 등록 발견!\n{title}\n{link}"

            send_telegram(msg)

            print("알림 전송:", title)


if __name__ == "__main__":
    check()
