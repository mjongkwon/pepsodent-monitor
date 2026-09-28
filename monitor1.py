import os
import re
import json
import requests

from playwright.sync_api import sync_playwright


# =========================================================
# 설정
# =========================================================

QUERY = "펩소덴트"
STORE_NAME = "공감 클릭"

# 🔴 GitHub Secrets
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 🔴 중복 알림 기록 파일
SEEN_FILE = "seen_products.json"


# =========================================================
# Telegram
# =========================================================

def send_telegram(message):

    if not BOT_TOKEN:
        print("❌ BOT_TOKEN이 없습니다.")
        return False

    if not CHAT_ID:
        print("❌ CHAT_ID가 없습니다.")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        response = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": message
            },
            timeout=20
        )

        print("Telegram 상태:", response.status_code)
        print("Telegram 응답:", response.text)

        if response.status_code == 200:
            print("✅ Telegram 전송 성공")
            return True

        print("❌ Telegram 전송 실패")
        return False

    except Exception as e:
        print("❌ Telegram 오류:", e)
        return False


# =========================================================
# 중복 알림 기록 읽기
# =========================================================

def load_seen_products():

    if not os.path.exists(SEEN_FILE):
        return set()

    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return set(data)

    except Exception as e:
        print("⚠️ 중복 기록 읽기 실패:", e)
        return set()


# =========================================================
# 중복 알림 기록 저장
# =========================================================

def save_seen_products(seen_products):

    try:

        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(
                sorted(list(seen_products)),
                f,
                ensure_ascii=False,
                indent=2
            )

        print("✅ 중복 기록 저장 완료")

    except Exception as e:
        print("❌ 중복 기록 저장 실패:", e)


# =========================================================
# 상품번호 추출
# =========================================================

def get_product_id(url):

    # 예:
    # https://smartstore.naver.com/xxx/products/8272697665

    match = re.search(r"/products/(\d+)", url)

    if match:
        return match.group(1)

    return ""


# =========================================================
# 네이버 쇼핑 검색
# =========================================================

def search_naver_shopping():

    search_url = (
        "https://search.shopping.naver.com/search/all"
        f"?query={QUERY}"
    )

    print("===================================")
    print("🔍 네이버 쇼핑 모니터링 시작")
    print("검색어:", QUERY)
    print("판매처:", STORE_NAME)
    print("===================================")

    print("네이버 쇼핑 주소:")
    print(search_url)

    products = []

    with sync_playwright() as p:

        # 🔴 Chromium 실행
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
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()

        try:

            print("🌐 네이버 쇼핑 접속 중...")

            response = page.goto(
                search_url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            if response:
                print(
                    "네이버 HTTP 상태:",
                    response.status
                )

            # 🔴 페이지가 상품을 로딩할 시간을 줍니다.
            page.wait_for_timeout(5000)

            print("현재 페이지:", page.url)
            print("페이지 제목:", page.title())

            # -------------------------------------------------
            # 차단 여부 확인
            # -------------------------------------------------

            body_text = page.locator("body").inner_text(
                timeout=10000
            )

            if "접근이 제한" in body_text:
                print("❌ 네이버에서 접근을 제한했습니다.")
                return []

            if "자동화" in body_text and "차단" in body_text:
                print("❌ 자동화 접근이 차단된 것으로 보입니다.")
                return []

            # -------------------------------------------------
            # 상품 링크 찾기
            # -------------------------------------------------

            links = page.locator(
                'a[href*="/products/"]'
            )

            count = links.count()

            print("상품 링크 발견:", count)

            # 같은 상품이 여러 번 나타나는 것을 방지
            found_ids = set()

            for i in range(count):

                try:

                    link_element = links.nth(i)

                    href = link_element.get_attribute(
                        "href"
                    )

                    if not href:
                        continue

                    # 상대주소 처리
                    if href.startswith("/"):
                        href = "https://smartstore.naver.com" + href

                    product_id = get_product_id(href)

                    if not product_id:
                        continue

                    # 이미 같은 상품을 처리했다면 건너뜀
                    if product_id in found_ids:
                        continue

                    found_ids.add(product_id)

                    # -------------------------------------------------
                    # 상품명
                    # -------------------------------------------------

                    title = link_element.inner_text().strip()

                    # 링크 자체에 상품명이 없는 경우
                    # 부모 영역의 텍스트를 가져옵니다.
                    if not title:

                        try:
                            parent = link_element.locator(
                                "xpath=.."
                            )

                            title = parent.inner_text().strip()

                        except:
                            title = ""

                    # -------------------------------------------------
                    # 주변 영역의 전체 텍스트
                    # 판매처 이름 확인용
                    # -------------------------------------------------

                    surrounding_text = ""

                    try:

                        # 몇 단계 위의 상품 영역을 확인
                        ancestor = link_element.locator(
                            "xpath=../../.."
                        )

                        surrounding_text = (
                            ancestor.inner_text()
                        )

                    except:
                        surrounding_text = ""

                    # -------------------------------------------------
                    # 검색어 확인
                    # -------------------------------------------------

                    if QUERY not in title and QUERY not in surrounding_text:
                        continue

                    # -------------------------------------------------
                    # 판매처 확인
                    # -------------------------------------------------

                    if STORE_NAME not in surrounding_text:

                        print(
                            "판매처 불일치:",
                            product_id,
                            title[:80]
                        )

                        continue

                    # -------------------------------------------------
                    # 상품 발견
                    # -------------------------------------------------

                    print("-----------------------------------")
                    print("🎉 상품 발견!")
                    print("상품명:", title)
                    print("판매처:", STORE_NAME)
                    print("상품번호:", product_id)
                    print("URL:", href)
                    print("-----------------------------------")

                    products.append({
                        "product_id": product_id,
                        "title": title,
                        "mall": STORE_NAME,
                        "link": href
                    })

                except Exception as e:

                    print(
                        "⚠️ 상품 하나 처리 중 오류:",
                        e
                    )

            print(
                "조건에 맞는 상품:",
                len(products)
            )

        except Exception as e:

            print("❌ 네이버 검색 오류:", e)

            # 디버깅용 스크린샷
            try:
                page.screenshot(
                    path="naver_error.png",
                    full_page=True
                )

                print(
                    "📸 nav er_error.png 저장"
                )

            except:
                pass

        finally:

            browser.close()

    return products


# =========================================================
# 메인
# =========================================================

def check():

    seen_products = load_seen_products()

    print(
        "기존 알림 상품:",
        len(seen_products)
    )

    products = search_naver_shopping()

    if not products:

        print(
            "현재 조건에 맞는 새 상품이 없습니다."
        )

        return

    new_products = 0

    for product in products:

        product_id = product["product_id"]

        # -------------------------------------------------
        # 🔴 이미 Telegram을 보낸 상품이면 건너뜁니다.
        # -------------------------------------------------

        if product_id in seen_products:

            print(
                "⏭️ 이미 알림한 상품:",
                product_id
            )

            continue

        message = (
            "📢 상품 등록 발견!\n\n"
            f"상품명: {product['title']}\n"
            f"판매처: {product['mall']}\n"
            f"상품번호: {product['product_id']}\n"
            f"상품 URL: {product['link']}"
        )

        print("📨 Telegram 전송:")
        print(message)

        # -------------------------------------------------
        # Telegram 전송 성공했을 때만
        # 중복 기록에 저장합니다.
        # -------------------------------------------------

        success = send_telegram(message)

        if success:

            seen_products.add(product_id)

            new_products += 1

            print(
                "✅ 새 상품 알림 완료:",
                product_id
            )

        else:

            print(
                "❌ Telegram 실패 - "
                "중복 기록에 저장하지 않음"
            )

    # -----------------------------------------------------
    # 중복 기록 저장
    # -----------------------------------------------------

    save_seen_products(seen_products)

    print(
        "새로 알림한 상품:",
        new_products
    )


# =========================================================
# 실행
# =========================================================

if __name__ == "__main__":
    check()

