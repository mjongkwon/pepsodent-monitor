import requests
import os
import json

# =========================================================
# 설정
# =========================================================

KEYWORD = "펩소덴트"
STORE_NAME = "공감 클릭"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


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
    else:
        print("❌ Telegram 알림 전송 실패")
        print(response.text)


# =========================================================
# 네이버플러스 스토어 검색
# =========================================================

def search_naver_plus_store():

    url = "https://ns-portal.shopping.naver.com/api/v2/shopping-paged-slot"

    params = {
        "query": KEYWORD,
        "source": "shp_gui"
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/130.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Referer": "https://search.shopping.naver.com/ns/search"
    }

    print()
    print("🌐 네이버플러스 스토어 검색")
    print("검색어:", KEYWORD)
    print("요청 URL:", url)

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=30
    )

    print("네이버 HTTP 상태:", response.status_code)

    if response.status_code != 200:

        print("❌ 네이버 검색 요청 실패")
        print(response.text[:2000])

        return None

    print("응답 크기:", len(response.text))

    return response.json()


# =========================================================
# 데이터에서 문자열 찾기
# =========================================================

def find_store(data):

    found = []

    def scan(obj):

        if isinstance(obj, dict):

            # 상품 데이터에서 흔히 사용되는 필드들을 확인
            title = str(
                obj.get("title", "")
                or obj.get("productName", "")
                or obj.get("name", "")
            )

            mall = str(
                obj.get("mallName", "")
                or obj.get("storeName", "")
                or obj.get("sellerName", "")
                or obj.get("mall", "")
            )

            # 펩소덴트 + 공감 클릭
            if KEYWORD in title and STORE_NAME in mall:

                found.append({
                    "title": title,
                    "mall": mall,
                    "data": obj
                })

            for value in obj.values():
                scan(value)

        elif isinstance(obj, list):

            for item in obj:
                scan(item)

    scan(data)

    return found


# =========================================================
# 메인
# =========================================================

def check():

    print()
    print("===================================")
    print("🔍 공감 클릭 SmartStore 모니터링")
    print("검색어:", KEYWORD)
    print("확인 스토어:", STORE_NAME)
    print("===================================")

    data = search_naver_plus_store()

    if data is None:
        return

    print()
    print("🔎 네이버플러스 스토어 응답 분석 중...")

    found = find_store(data)

    print()
    print("===================================")
    print("조건에 맞는 상품:", len(found))
    print("===================================")

    if not found:

        print("현재 공감 클릭에서 펩소덴트 상품을 찾지 못했습니다.")

        # 테스트를 위해 응답 구조의 일부를 출력
        print()
        print("----- 응답 구조 확인용 -----")
        print(json.dumps(data, ensure_ascii=False)[:5000])

        return

    # =====================================================
    # 발견
    # =====================================================

    for product in found:

        title = product["title"]

        print()
        print("🎯 펩소덴트 상품 발견!")
        print("상품명:", title)
        print("스토어:", product["mall"])

        message = (
            "📢 펩소덴트 상품 발견!\n\n"
            f"스토어: {STORE_NAME}\n"
            f"상품명: {title}"
        )

        send_telegram(message)


if __name__ == "__main__":
    check()
