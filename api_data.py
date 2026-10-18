import gc, urequests

WORKER_URL = "https://noisy-mountain-aa11.amjavadi.workers.dev/"

# نگاشت کلیدهای ورکر به عنوان نمایشی روی ماتریس
ITEM_LABELS = {
    # طلا و سکه
    "geram18": "GOLD", "abshodeh": "ABSHODEH", "emami": "EMAMI", "ons": "ONS",
    # ارزها
    "usd_sell": "USD", "usd_ist": "USD-IST", "eur": "EUR", "aed": "AED",
    "try": "TRY", "gbp": "GBP", "cny": "CNY", "cad": "CAD", "aud": "AUD",
    "rub": "RUB", "iqd": "IQD", "myr": "MYR", "gel": "GEL", "azn": "AZN",
    "amd": "AMD", "thb": "THB", "omr": "OMR", "inr": "INR", "jpy": "JPY", "afn": "AFN",
    # کریپتو
    "usdt": "USDT", "btc": "BTC", "eth": "ETH", "bnb": "BNB", "shib": "SHIB",
    "doge": "DOGE", "ton": "TON", "not": "NOT", "xrp": "XRP"
}

def fetch_market_data():
    """دریافت یکجای ۳۳ قلم بازار از ورکر کلودفلر"""
    gc.collect()
    try:
        res = urequests.get(WORKER_URL, timeout=8)
        data = res.json()
        res.close()
        gc.collect()
        return data if isinstance(data, dict) else {}
    except:
        return {}

def fetch_weather():
    gc.collect()
    try:
        res = urequests.get("http://api.open-meteo.com/v1/forecast?latitude=35.6892&longitude=51.3890&current=temperature_2m", timeout=6)
        data = res.json()
        res.close()
        return f"{round(data['current']['temperature_2m'])}C"
    except:
        return "--C"

def fetch_oil():
    gc.collect()
    try:
        res = urequests.get("https://query1.finance.yahoo.com/v8/finance/chart/BZ=F?interval=1d&range=1d", headers={'User-Agent':'Mozilla/5.0'}, timeout=6)
        data = res.json()
        res.close()
        price = float(data['chart']['result'][0]['meta']['regularMarketPrice'])
        return f"OIL:{price:.2f}$"
    except:
        return "OIL:ERR"

# توابع کمکی برای سازگاری عقب‌رو (Backward Compatibility)
def fetch_usdt(market_data=None):
    if market_data and "usdt" in market_data:
        return f"USDT:{market_data['usdt']}"
    return "USDT:ERR"

def fetch_gold(market_data=None):
    if market_data and "geram18" in market_data:
        return f"GOLD:{market_data['geram18']}"
    return "GOLD:ERR"

def fetch_btc(market_data=None):
    if market_data and "btc" in market_data:
        return f"BTC:{market_data['btc']}"
    return "BTC:ERR"

