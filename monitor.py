import requests
import json
import os
from datetime import datetime, timezone, timedelta

# ===== 설정 =====
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

query = "펩소덴트"
store_name = "공감 클릭"

bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

data_file = "sent_items.json"

# 24시간마다 다시 알림
ALERT_INTERVAL = timedelta(hours=24)
# =================


def send_telegram(msg):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": msg
        }
    )

    response.raise_for_status()


def load_sent():
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)

    return {}


def save_sent(data):
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def check():
    url = "https://openapi.naver.com/v1/search/shop"

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }

    params = {
        "query": query,
        "display": 10
    }

    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()

    items = res.json().get("items", [])

    sent_data = load_sent()

    now = datetime.now(timezone.utc)

    for item in items:
        title = item["title"]
        mall = item["mallName"]
        link = item["link"]

        # HTML 태그 제거
        clean_title = title.replace("<b>", "").replace("</b>", "")

        # 펩소덴트 + 공감 클릭 상품인지 확인
        if query in clean_title and store_name in mall:

            # 상품명 + 쇼핑몰명을 식별자로 사용
            key = clean_title + "||" + mall

            # 이전 알림 시간 확인
            last_sent = sent_data.get(key)

            should_send = False

            if last_sent is None:
                # 처음 발견
                should_send = True

            else:
                # 마지막 알림으로부터 24시간 경과했는지 확인
                last_sent_time = datetime.fromisoformat(last_sent)

                if now - last_sent_time >= ALERT_INTERVAL:
                    should_send = True

            if should_send:

                msg = (
                    f"📢 펩소덴트 상품 확인!\n"
                    f"{clean_title}\n"
                    f"{link}"
                )

                send_telegram(msg)

                # 이번 알림 시간을 기록
                sent_data[key] = now.isoformat()

                save_sent(sent_data)

                print("알림 전송:", clean_title)

            else:
                print("24시간 이내 알림 전송:", clean_title)

    # 알림이 없어도 현재 데이터는 유지
    save_sent(sent_data)


if __name__ == "__main__":
    check()
