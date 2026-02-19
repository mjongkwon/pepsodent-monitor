import requests

# ===== 설정 =====
client_id = "k4d5tzosRsvc1fhHPbmL"
client_secret = "AV7PkWkrIe"
query = "펩소덴트"
store_name = "공감 클릭"

bot_token = "8512854707:AAFY-YfNuQk97Gl-NEn7M4lp5yxS9e9qx7k"
chat_id = "8272697665"
# =================

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

def check_product():
    url = "https://openapi.naver.com/v1/search/shop.json"

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }

    params = {"query": query, "display": 10}

    res = requests.get(url, headers=headers, params=params)
    data = res.json()

    for item in data.get("items", []):
        title = item.get("title", "")
        mall = item.get("mallName", "")
        link = item.get("link", "")

        if query in title and store_name in mall:
            send_telegram(f"📢 상품 발견!\n{title}\n{link}")
            break

if __name__ == "__main__":
    check_product()
