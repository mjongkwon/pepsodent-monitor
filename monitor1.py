import requests
import os
import re
import json


# =========================================================
# 🔴 여기만 확인하세요
# =========================================================

QUERY = "펩소덴트"
STORE_NAME = "공감 클릭"

# GitHub Secrets
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SEEN_FILE = "seen_products.json"


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

    print("Telegram 상태:", response.status_code)

    return response.ok


# =========================================================
# 기존에 알림 보낸 상품
# =========================================================

def load_seen_products():

    if not os.path.exists(SEEN_FILE):
        return set()

    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))

    except Exception:
        return set()


def save_seen_products(seen):

    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(
            sorted(seen),
            f,
            ensure_ascii=False,
            indent=2
        )


# =========================================================
# 상품번호 추출
# =========================================================

def get_product_id(url):

    if not url:
        return None

    # Smartstore 상품번호
    match = re.search(r"/products/(\d+)", url)

    if match:
        return match.group(1)

    return None


# =========================================================
# 네이버 일반 검색 API
# =========================================================

def search_naver():

    url = "https://openapi.naver.com/v1/search/webkr.json"

    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }

    # 🔴 검색어
    search_query = f"{QUERY} {STORE_NAME}"

    params = {
        "query": search_query,
        "display": 100,
        "start": 1,
        "sort": "date"
    }

    print()
    print("🌐 네이버 일반 검색 API")
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

    products = []

    for item in items:

        title = item.get("title", "")
        link = item.get("link", "")
        description = item.get("description", "")

                print()
        print("----- 검색 결과 -----")
        print("제목:", title)
        print("URL:", link)
        print("설명:", description)

        # HTML 태그 제거
        title = re.sub(r"<.*?>", "", title)
        description = re.sub(r"<.*?>", "", description)

        text = title + " " + description

        # -------------------------------------------------
        # 펩소덴트가 포함되어 있어야 함
        # -------------------------------------------------

        if QUERY not in text:
            continue

        # -------------------------------------------------
        # 공감 클릭이 포함되어 있어야 함
        # -------------------------------------------------

        if STORE_NAME not in text:
            continue

        # -------------------------------------------------
        # 상품번호 추출
        # -------------------------------------------------

        product_id = get_product_id(link)

        if not product_id:
            continue

        products.append({
            "id": product_id,
            "title": title,
            "url": link
        })

    return products


# =========================================================
# 메인
# =========================================================

def check():

    seen = load_seen_products()

    print()
    print("기존 알림 상품:", len(seen))

    print()
    print("===================================")
    print("🔍 네이버 상품 모니터링 시작")
    print("검색어:", QUERY)
    print("판매처:", STORE_NAME)
    print("===================================")

    products = search_naver()

    print()
    print("조건에 맞는 상품:", len(products))

    new_products = []

    for product in products:

        product_id = product["id"]

        if product_id in seen:
            continue

        new_products.append(product)

    # -----------------------------------------------------
    # 새 상품 발견
    # -----------------------------------------------------

    for product in new_products:

        message = (
            "📢 새로운 상품 발견!\n\n"
            f"상품명: {product['title']}\n"
            f"상품번호: {product['id']}\n"
            f"상품주소: {product['url']}"
        )

        print()
        print("📢 새 상품:", product["title"])
        print("상품번호:", product["id"])
        print("URL:", product["url"])

        success = send_telegram(message)

        if success:
            seen.add(product["id"])

    # -----------------------------------------------------
    # 저장
    # -----------------------------------------------------

    save_seen_products(seen)

    if new_products:
        print()
        print("새 상품:", len(new_products))
    else:
        print()
        print("현재 조건에 맞는 새 상품이 없습니다.")


if __name__ == "__main__":
    check()
