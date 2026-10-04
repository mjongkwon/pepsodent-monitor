import requests
import os
import re


# =========================================================
# 🔴 설정
# =========================================================

# 모니터링할 SmartStore
STORE_ID = "smart_how"

# 찾을 상품명
KEYWORD = "펩소덴트"

# GitHub Secrets
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
        return True

    print("❌ Telegram 알림 전송 실패")
    print(response.text)

    return False


# =========================================================
# 네이버 웹문서 검색
# =========================================================

def search_naver():

    url = "https://openapi.naver.com/v1/search/webkr.json"

    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }

    # 🔴 핵심 검색어
    #
    # SmartStore의 특정 스토어 안에서
    # 펩소덴트를 찾도록 검색
    search_query = f"site:smartstore.naver.com/{STORE_ID} {KEYWORD}"

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
# 상품 검색
# =========================================================

def check():

    print()
    print("===================================")
    print("🔍 공감 클릭 SmartStore 모니터링")
    print("스토어 ID:", STORE_ID)
    print("검색어:", KEYWORD)
    print("===================================")

    items = search_naver()

    found_products = []

    for item in items:

        title = item.get("title", "")
        link = item.get("link", "")
        description = item.get("description", "")

        # HTML 태그 제거
        title = re.sub(r"<.*?>", "", title)
        description = re.sub(r"<.*?>", "", description)

        print()
        print("----- 검색 결과 -----")
        print("제목:", title)
        print("URL:", link)
        print("설명:", description)

        # -------------------------------------------------
        # SmartStore 주소인지 확인
        # -------------------------------------------------

        if f"smartstore.naver.com/{STORE_ID}" not in link:
            continue

        # -------------------------------------------------
        # 펩소덴트가 제목 또는 설명에 있는지 확인
        # -------------------------------------------------

        text = f"{title} {description}"

        if KEYWORD not in text:
            continue

        # -------------------------------------------------
        # 상품 URL인지 확인
        # -------------------------------------------------

        if "/products/" not in link:
            continue

        found_products.append({
            "title": title,
            "url": link
        })

    # =====================================================
    # 결과
    # =====================================================

    print()
    print("===================================")
    print("조건에 맞는 상품:", len(found_products))
    print("===================================")

    if not found_products:

        print("현재 펩소덴트 상품이 검색되지 않았습니다.")
        return

    # =====================================================
    # Telegram 알림
    #
    # 🔴 중복 검사 없음
    # 🔴 저장 없음
    # 🔴 매번 발견하면 알림
    # =====================================================

    for product in found_products:

        message = (
            "📢 펩소덴트 상품 발견!\n\n"
            f"상품명: {product['title']}\n\n"
            f"상품 URL:\n{product['url']}"
        )

        print()
        print("📢 Telegram 알림:")
        print(product["title"])
        print(product["url"])

        send_telegram(message)


# =========================================================
# 실행
# =========================================================

if __name__ == "__main__":
    check()
