import gc, urequests
def fetch_weather():
    gc.collect()
    try:
        res=urequests.get("http://api.open-meteo.com/v1/forecast?latitude=35.6892&longitude=51.3890&current=temperature_2m",timeout=6)
        data=res.json(); res.close(); return f"{round(data['current']['temperature_2m'])}C"
    except: return "--C"
def fetch_usdt():
    gc.collect()
    try:
        res=urequests.get("https://api.wallex.ir/v1/depth?symbol=USDTTMN",headers={'User-Agent':'Mozilla/5.0'},timeout=6)
        data=res.json(); res.close(); price=int(float(data['result']['bid'][0]['price']))
        return f"USDT:{price:,}T"
    except: return "USDT:ERR"
def fetch_gold():
    gc.collect()
    try:
        res = urequests.get("https://api.wallex.ir/v1/depth?symbol=PAXGTMN", headers={'User-Agent': 'Mozilla/5.0'}, timeout=6)
        data = res.json()
        res.close()
        # محاسبه قیمت کل و سپس حذف ۳ رقم آخر (تقسیم بر ۱۰۰۰)
        gold_raw = int(float(data['result']['bid'][0]['price']) * 0.0241144)
        gold_short = gold_raw // 1000  # مثلاً 4,650,000 تبدیل میشه به 4650
        return f"GOLD:{gold_short:,}T"
    except:
        return "GOLD:ERR"
    
def fetch_btc():
    gc.collect()
    try:
        res=urequests.get("https://api.wallex.ir/v1/depth?symbol=BTCUSDT",headers={'User-Agent':'Mozilla/5.0'},timeout=6)
        data=res.json(); res.close(); price=int(float(data['result']['bid'][0]['price']))
        return f"BTC:{price:,}$"
    except: return "BTC:ERR"
def fetch_oil():
    gc.collect()
    try:
        res=urequests.get("https://query1.finance.yahoo.com/v8/finance/chart/BZ=F?interval=1d&range=1d",headers={'User-Agent':'Mozilla/5.0'},timeout=6)
        data=res.json(); res.close(); price=float(data['chart']['result'][0]['meta']['regularMarketPrice'])
        return f"OIL:{price:.2f}$"
    except: return "OIL:ERR"
