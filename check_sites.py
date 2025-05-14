import requests
import sys
import time
from datetime import datetime

# Конфигурация Telegram
TELEGRAM_TOKEN = "7603803205:AAEh3XXgXPlWRnu-rMC0Okl-9gPFgkobNXk"
CHAT_ID = "-4696089033"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def send_telegram_alert(message):
    try:
        response = requests.post(
            TELEGRAM_API_URL,
            json={
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            },
            timeout=15
        )
        return response.json().get('ok', False)
    except Exception as e:
        print(f"Ошибка отправки в TG: {str(e)}", file=sys.stderr)
        return False

def check_design(url, expected_try_new, design_name):
    try:
        response = requests.get(url, allow_redirects=True, timeout=20)
        final_url = response.url
        content = response.text
        has_try_new = "try_new" in content

        if has_try_new == expected_try_new:
            print(f"[УСПЕХ] {datetime.now()} - {design_name} {url} → {final_url} | 'try_new' найден: {has_try_new} (ожидалось: {expected_try_new})")
            return True
        else:
            print(f"[ОШИБКА] {datetime.now()} - {design_name} {url} → {final_url} | 'try_new' найден: {has_try_new} (ожидалось: {expected_try_new})", file=sys.stderr)
            return False
    except Exception as e:
        print(f"[КРИТИЧЕСКАЯ ОШИБКА] {datetime.now()} - {design_name} {url}: {str(e)}", file=sys.stderr)
        return False

def check_redirect_status(url, design_name):
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        final_url = response.url
        history = [r.url for r in response.history]
        
        if response.history:
            print(f"[УСПЕХ] {datetime.now()} - {design_name} {url} → Редирект работает. История: {history} → {final_url} (Код: {response.status_code})")
            return True
        else:
            print(f"[ОШИБКА] {datetime.now()} - {design_name} {url} → Нет редиректа. Конечный URL: {final_url} (Код: {response.status_code})", file=sys.stderr)
            return False
    except Exception as e:
        print(f"[КРИТИЧЕСКАЯ ОШИБКА] {datetime.now()} - {design_name} {url}: {str(e)}", file=sys.stderr)
        return False

# Настройки
SITES = {
    "old_design": {
        "url": "https://upx-l.tech/t7ebd9028",
        "name": "старый дизайн",
        "check_func": check_design,
        "params": {"expected_try_new": True, "design_name": "старый дизайн"}
    },
    "new_design": {
        "url": "https://upx-l.tech/tbcafa1ba",
        "name": "новый дизайн",
        "check_func": check_design,
        "params": {"expected_try_new": False, "design_name": "новый дизайн"}
    },
    "getx": {
        "url": "https://levelx.top/t2f4d1e32",
        "name": "GET-X",
        "check_func": check_redirect_status,
        "params": {"design_name": "GET-X"}
    }
}

CHECK_INTERVAL = 3600  # 1 час

while True:
    print(f"\n=== Проверка начата: {datetime.now()} ===")
    
    results = {}
    getx_result = None  # Для отдельного сообщения GET-X
    
    for site_name, site_data in SITES.items():
        results[site_name] = site_data["check_func"](site_data["url"], **site_data["params"])
        print(f"{site_data['name']} - {'✅' if results[site_name] else '❌'}")
        
        # Сохраняем результат GET-X отдельно
        if site_name == "getx":
            getx_result = results[site_name]

    # Формируем основное сообщение (только дизайны)
    message_lines = []
    designs_ok = all([results["old_design"], results["new_design"]])  # Исправлено: передаем список
    
    if designs_ok:
        message_lines.append("✅ *Ссылки работают:*")
    else:
        message_lines.append("❌ *Проблемы с ссылками:*")
    
    for site_name in ["old_design", "new_design"]:
        site_data = SITES[site_name]
        status = "работает" if results[site_name] else "не работает"
        message_lines.append(f"- {site_data['name']} - {status} - {site_data['url']}")

    # Отправляем основное сообщение
    main_message = "\n".join(message_lines)
    print(main_message)
    send_telegram_alert(main_message)

    # Отправляем отдельное сообщение для GET-X
    getx_status = "работает" if getx_result else "не работает"
    getx_message = f"✅ *Ссылка работает* - {SITES['getx']['url']}"
    print(f"\n{getx_message}")
    send_telegram_alert(getx_message)

    print(f"\n=== Проверка завершена. Следующая проверка через {CHECK_INTERVAL//3600} ч ===")
    time.sleep(CHECK_INTERVAL)