import requests
import os
import re

# =========================================================
# 설정
# =========================================================

KEYWORD = "펩소덴트"
STORE_NAME = "공감 클릭"

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# =========================================================
# Telegram 알림
# =========================================================

def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=30
    )

    print("Telegram HTTP 상태:", response.status_code)

    if response.ok:
        print("✅ Telegram 알림 전송 성공")
    else:
        print("❌ Telegram 알림 전송 실패")
        print(response.text)


# =========================================================
# 네이버 웹문서 검색
# =========================================================

def search_naver():

    url = "https://openapi.naver.com/v1/search/webkr.json"

    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }

    # 공감 클릭 + 펩소덴트 검색
    search_query = f'"{STORE_NAME}" "{KEYWORD}"'

    params = {
        "query": search_query,
        "display": 100,
        "start": 1
    }

    print()
    print("🌐 네이버 웹문서 검색 API")
    print("검색어:", search_query)

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30
    )

    print("네이버 HTTP 상태:", response.status_code)

    if response.status_code != 200:
        print("❌ 네이버 API 오류")
        print(response.text)
        return []

    data = response.json()

    items = data.get("items", [])

    print("검색 결과:", len(items))

    return items


# =========================================================
# 공감 클릭 + 펩소덴트 확인
# =========================================================

def check():

    print()
    print("===================================")
    print("🔍 공감 클릭 SmartStore 모니터링")
    print("검색어:", KEYWORD)
    print("확인 대상:", STORE_NAME)
    print("===================================")

    items = search_naver()

    found = False

    for item in items:

        title = item.get("title", "")
        description = item.get("description", "")
        link = item.get("link", "")

        # HTML 태그 제거
        title = re.sub(r"<.*?>", "", title)
        description = re.sub(r"<.*?>", "", description)

        print()
        print("----- 검색 결과 -----")
        print("제목:", title)
        print("URL:", link)
        print("설명:", description)

        # 제목 + 설명을 합쳐서 확인
        text = f"{title} {description}"

        # 공감 클릭 + 펩소덴트가 모두 있는지 확인
        if STORE_NAME in text and KEYWORD in text:

            found = True

            print()
            print("🎯 공감 클릭 + 펩소덴트 발견!")

            message = (
                "📢 펩소덴트 검색 결과 발견!\n\n"
                f"스토어: {STORE_NAME}\n"
                f"검색어: {KEYWORD}\n\n"
                f"제목: {title}\n"
                f"URL: {link}"
            )

            send_telegram(message)

    # =====================================================
    # 결과
    # =====================================================

    print()
    print("===================================")

    if found:
        print("🎯 조건에 맞는 검색 결과를 발견했습니다.")
    else:
        print("현재 '공감 클릭 + 펩소덴트' 검색 결과가 없습니다.")

    print("===================================")


if __name__ == "__main__":
    check()
