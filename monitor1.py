import os
import re
import requests

from playwright.sync_api import sync_playwright


# =========================================================
# 🔴 설정
# =========================================================

STORE_URL = "https://smartstore.naver.com/smart_how"
KEYWORD = "펩소덴트"

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
# SmartStore 확인
# =========================================================

def check_store():

    print()
    print("===================================")
    print("🔍 공감 클릭 SmartStore 모니터링")
    print("스토어:", STORE_URL)
    print("검색어:", KEYWORD)
    print("===================================")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        context = browser.new_context(
            locale="ko-KR",
            viewport={
                "width": 1440,
                "height": 1000
            },
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()

        print()
        print("🌐 SmartStore 접속 중...")

        try:

            response = page.goto(
                STORE_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            if response:
                print("HTTP 상태:", response.status)

            print("현재 URL:", page.url)
            print("페이지 제목:", page.title())

            # JavaScript로 상품 목록이 표시될 시간을 줌
            page.wait_for_timeout(5000)

        except Exception as e:

            print("❌ SmartStore 접속 실패")
            print(e)

            browser.close()
            return

        # -------------------------------------------------
        # 페이지 전체 텍스트 확인
        # -------------------------------------------------

        body_text = page.locator("body").inner_text()

        print()
        print("페이지 텍스트 길이:", len(body_text))

        # -------------------------------------------------
        # 🔴 펩소덴트가 페이지에 있는지 확인
        # -------------------------------------------------

        if KEYWORD not in body_text:

            print()
            print(f"❌ '{KEYWORD}'를 찾지 못했습니다.")

            # 디버깅용 페이지 정보
            print()
            print("페이지 앞부분:")
            print(body_text[:1000])

            browser.close()
            return

        print()
        print(f"🎯 '{KEYWORD}' 발견!")

        # -------------------------------------------------
        # 상품 링크 찾기
        # -------------------------------------------------

        links = page.locator("a").all()

        found_products = []

        for link in links:

            try:

                text = link.inner_text().strip()
                href = link.get_attribute("href")

                if not href:
                    continue

                if KEYWORD not in text:
                    continue

                # 상대 URL이면 SmartStore 주소 붙이기
                if href.startswith("/"):
                    href = "https://smartstore.naver.com" + href

                found_products.append({
                    "title": text,
                    "url": href
                })

            except Exception:
                continue

        # -------------------------------------------------
        # 결과
        # -------------------------------------------------

        print()
        print("펩소덴트 관련 링크:", len(found_products))

        # 중복 URL 제거
        unique_products = {}

        for product in found_products:

            unique_products[product["url"]] = product["title"]

        # -------------------------------------------------
        # Telegram
        # -------------------------------------------------

        if unique_products:

            for url, title in unique_products.items():

                message = (
                    "📢 펩소덴트 상품 발견!\n\n"
                    f"상품명: {title}\n\n"
                    f"상품 URL:\n{url}"
                )

                send_telegram(message)

        else:

            # 페이지에는 펩소덴트가 있지만 링크를 찾지 못한 경우
            print()
            print("⚠️ 펩소덴트 문구는 발견했지만 상품 링크를 찾지 못했습니다.")

            message = (
                "⚠️ 펩소덴트 발견\n\n"
                "공감 클릭 SmartStore 페이지에서 "
                "펩소덴트 문구는 발견했지만 상품 URL을 추출하지 못했습니다.\n\n"
                f"{STORE_URL}"
            )

            send_telegram(message)

        browser.close()


# =========================================================
# 실행
# =========================================================

if __name__ == "__main__":
    check_store()
