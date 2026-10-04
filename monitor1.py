import os
import requests


# =========================================================
# 설정
# =========================================================

KEYWORD = "펩소덴트"
STORE_NAME = "공감 클릭"

APIFY_TOKEN = os.getenv("APIFY_TOKEN")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# Apify Actor
ACTOR_ID = "silentflow~naver-scraper"

APIFY_URL = (
    f"https://api.apify.com/v2/actors/"
    f"{ACTOR_ID}/run-sync-get-dataset-items"
)


# =========================================================
# Telegram
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
# Apify → Naver Shopping 검색
# =========================================================

def search_naver():

    print()
    print("===================================")
    print("🌐 Apify Naver Shopping 검색")
    print("검색어:", KEYWORD)
    print("===================================")

    headers = {
        "Authorization": f"Bearer {APIFY_TOKEN}",
        "Content-Type": "application/json"
    }

    # 하루 한 번 검색하는 것이므로
    # 필요한 정도의 상품만 가져옵니다.
    payload = {
        "keywords": [
            KEYWORD
        ],
        "maxItems": 90,
        "includeDetails": False,
        "maxReviews": 0
    }

    response = requests.post(
        APIFY_URL,
        headers=headers,
        json=payload,
        timeout=300
    )

    print("Apify HTTP 상태:", response.status_code)

    # 200뿐 아니라 201 등 모든 2xx를 정상 처리
    if not response.ok:
        
        print("❌ Apify 오류")
        print(response.text[:5000])

        return []

    try:
        items = response.json()

    except Exception as e:

        print("❌ JSON 변환 실패")
        print(str(e))

        return []

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
    print("확인 스토어:", STORE_NAME)
    print("===================================")

    items = search_naver()

    found = []

    for item in items:

        title = str(item.get("title", ""))
        store_name = str(item.get("storeName", ""))
        store_url = str(item.get("storeUrl", ""))

        print()
        print("----- 상품 -----")
        print("상품명:", title)
        print("스토어:", store_name)

        # -------------------------------------------------
        # 펩소덴트 + 공감 클릭
        # -------------------------------------------------

        if KEYWORD in title and STORE_NAME.strip() in store_name:

            found.append({
                "title": title,
                "store_name": store_name,
                "store_url": store_url
            })

    # =====================================================
    # 결과
    # =====================================================

    print()
    print("===================================")
    print("조건에 맞는 상품:", len(found))
    print("===================================")

    if not found:

        print(
            f"현재 '{STORE_NAME}'에서 "
            f"'{KEYWORD}' 상품을 찾지 못했습니다."
        )

        return

    # =====================================================
    # Telegram
    # =====================================================

    for product in found:

        message = (
            "📢 펩소덴트 상품 발견!\n\n"
            f"스토어: {product['store_name']}\n"
            f"상품명: {product['title']}\n\n"
            f"스토어 URL:\n{product['store_url']}"
        )

        print()
        print("🎯 상품 발견!")
        print("상품명:", product["title"])
        print("스토어:", product["store_name"])

        send_telegram(message)


# =========================================================
# 실행
# =========================================================

if __name__ == "__main__":
    check()
