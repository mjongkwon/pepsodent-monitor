import os
import requests
from playwright.sync_api import sync_playwright

# =========================================================
# 설정
# =========================================================

KEYWORD = "펩소덴트"
STORE_NAME = "공감 클릭"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SEARCH_URL = (
    "https://search.shopping.naver.com/ns/search"
    "?query=펩소덴트"
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
    else:
        print("❌ Telegram 알림 전송 실패")
        print(response.text)


# =========================================================
# 네이버플러스 스토어 검색
# =========================================================

def check():

    print()
    print("===================================")
    print("🔍 공감 클릭 SmartStore 모니터링")
    print("검색어:", KEYWORD)
    print("확인 스토어:", STORE_NAME)
    print("===================================")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page(
            viewport={
                "width": 1440,
                "height": 1200
            },
            locale="ko-KR"
        )

        print()
        print("🌐 네이버플러스 스토어 접속")
        print(SEARCH_URL)

        try:

            response = page.goto(
                SEARCH_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            print("페이지 HTTP 상태:",
                  response.status if response else "없음")

            # 검색 결과가 렌더링될 시간을 줌
            page.wait_for_timeout(7000)

            print("현재 URL:")
            print(page.url)

            print()
            print("페이지 제목:")
            print(page.title())

            # 화면에 표시된 전체 텍스트
            body_text = page.locator("body").inner_text()

            print()
            print("페이지 텍스트 길이:",
                  len(body_text))

            print()
            print("----- 페이지 텍스트 앞부분 -----")
            print(body_text[:8000])

            # =================================================
            # 핵심 검사
            # =================================================

            keyword_found = KEYWORD in body_text
            store_found = STORE_NAME in body_text

            print()
            print("===================================")
            print("펩소덴트 발견:", keyword_found)
            print("공감 클릭 발견:", store_found)
            print("===================================")

            if keyword_found and store_found:

                print()
                print("🎯 공감 클릭 + 펩소덴트 발견!")

                message = (
                    "📢 펩소덴트 상품 발견!\n\n"
                    f"스토어: {STORE_NAME}\n"
                    f"검색어: {KEYWORD}\n\n"
                    "네이버플러스 스토어 검색 결과에서 "
                    "공감 클릭 상품이 확인되었습니다."
                )

                send_telegram(message)

            else:

                print()
                print("현재 조건에 맞는 상품이 없습니다.")

        except Exception as e:

            print()
            print("❌ 브라우저 실행 중 오류")
            print(type(e).__name__)
            print(str(e))

        finally:

            browser.close()


if __name__ == "__main__":
    check()
