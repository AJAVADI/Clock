import network, socket, time, machine
from config import save_config

# تابع unquote برای دیکُد کردن پارامترهای URL-encoded
def unquote(string):
    res = string.replace('+', ' ')
    parts = res.split('%')
    if len(parts) == 1:
        return res
    output = parts[0]
    for part in parts[1:]:
        if len(part) >= 2:
            try:
                output += chr(int(part[:2], 16)) + part[2:]
            except:
                output += '%' + part
        else:
            output += '%' + part
    return output

# تابع parse_form_data برای تبدیل داده‌های فرم به دیکشنری
def parse_form_data(body):
    data = {}
    for pair in body.split('&'):
        if '=' in pair:
            k, v = pair.split('=', 1)
            data[unquote(k)] = unquote(v)
    return data

# تابع render_html برای ساخت صفحه تنظیمات
def render_html(cfg):
    checked = lambda val: 'checked' if val else ''
    return f'''<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Clock Settings</title>
<style>
    * {{box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}}
    body {{background:#0f172a;color:#f8fafc;margin:0;padding:20px}}
    .card {{background:#1e293b;max-width:440px;margin:0 auto;padding:24px;border-radius:14px;box-shadow:0 10px 25px rgba(0,0,0,.5)}}
    h2 {{margin-top:0;text-align:center;color:#38bdf8;font-size:22px}}
    .group {{margin-bottom:18px}}
    label {{display:block;margin-bottom:6px;font-weight:600;font-size:14px}}
    input[type="text"],input[type="password"],input[type="number"] {{width:100%;padding:10px 12px;background:#334155;border:1px solid #475569;border-radius:8px;color:#fff;font-size:15px;outline:none}}
    input:focus {{border-color:#38bdf8}}
    .check-group {{display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid #334155}}
    .check-group label {{margin-bottom:0;cursor:pointer}}
    input[type="checkbox"] {{transform:scale(1.3);cursor:pointer;accent-color:#38bdf8}}
    .btn {{width:100%;padding:12px;background:#0284c7;border:0;border-radius:8px;color:#fff;font-size:16px;font-weight:bold;cursor:pointer;margin-top:18px}}
    .desc {{font-size:12px;color:#94a3b8;text-align:center;margin-top:12px}}
</style></head><body><div class="card"><h2>تنظیمات ساعت هوشمند</h2><form method="POST" action="/save">
<div class="group"><label>نام وای‌فای (SSID):</label><input type="text" name="wifi_ssid" value="{cfg.get('wifi_ssid','')}" required dir="ltr"></div>
<div class="group"><label>رمز وای‌فای (Password):</label><input type="password" name="wifi_pass" value="{cfg.get('wifi_pass','')}" dir="ltr"></div>
<div class="group"><label>شدت نور ماتریس (0 تا 15):</label><input type="number" name="brightness" min="0" max="15" value="{cfg.get('brightness',2)}"></div>
<div class="group"><label>بازه بروزرسانی داده‌ها (ثانیه):</label><input type="number" name="fetch_interval" min="30" max="3600" value="{cfg.get('fetch_interval',120)}"></div>
<div style="margin-top:15px;margin-bottom:5px;font-weight:bold;color:#38bdf8">نمایش بخش‌ها:</div>
<div class="check-group"><label for="show_date">تاریخ شمسی</label><input type="checkbox" id="show_date" name="show_date" {checked(cfg.get('show_date',True))}></div>
<div class="check-group"><label for="show_usdt">قیمت تتر (USDT)</label><input type="checkbox" id="show_usdt" name="show_usdt" {checked(cfg.get('show_usdt',True))}></div>
<div class="check-group"><label for="show_gold">طلای ۱۸ عیار (GOLD)</label><input type="checkbox" id="show_gold" name="show_gold" {checked(cfg.get('show_gold',True))}></div>
<div class="check-group"><label for="show_btc">بیت‌کوین (BTC)</label><input type="checkbox" id="show_btc" name="show_btc" {checked(cfg.get('show_btc',True))}></div>
<div class="check-group"><label for="show_oil">نفت (OIL)</label><input type="checkbox" id="show_oil" name="show_oil" {checked(cfg.get('show_oil',True))}></div>
<div class="check-group"><label for="show_weather">دمای هوای تهران</label><input type="checkbox" id="show_weather" name="show_weather" {checked(cfg.get('show_weather',True))}></div>
<button type="submit" class="btn">ذخیره و راه‌اندازی مجدد</button><div class="desc">پس از ذخیره، برد ریستارت شده و به شبکه وصل می‌شود.</div></form></div></body></html>'''

# تابع draw_compact_ip برای رسم IP فشرده روی نمایشگر
def draw_compact_ip(display, ip_str):
    display.fill(0)
    FONT_3x7 = {
        '0': [0b111,0b101,0b101,0b101,0b101,0b101,0b111],
        '1': [0b010,0b110,0b010,0b010,0b010,0b010,0b111],
        '2': [0b111,0b001,0b001,0b111,0b100,0b100,0b111],
        '3': [0b111,0b001,0b001,0b111,0b001,0b001,0b111],
        '4': [0b101,0b101,0b101,0b111,0b001,0b001,0b001],
        '5': [0b111,0b100,0b100,0b111,0b001,0b001,0b111],
        '6': [0b111,0b100,0b100,0b111,0b101,0b101,0b111],
        '7': [0b111,0b001,0b001,0b010,0b010,0b100,0b100],
        '8': [0b111,0b101,0b101,0b111,0b101,0b101,0b111],
        '9': [0b111,0b101,0b101,0b111,0b001,0b001,0b111],
    }
    w = 0
    for ch in ip_str:
        w += 2 if ch == '.' else 4
    x = max(0, (64 - w) // 2)
    for ch in ip_str:
        if ch == '.':
            display.pixel(x, 6, 1)
            x += 2
        else:
            bm = FONT_3x7.get(ch)
            if bm:
                for row in range(7):
                    bits = bm[row]
                    if bits & 0b100: display.pixel(x,     row, 1)
                    if bits & 0b010: display.pixel(x + 1, row, 1)
                    if bits & 0b001: display.pixel(x + 2, row, 1)
            x += 4
    display.show()

# تابع start_ap_portal برای مدیریت حالت Access Point
# تابع start_ap_portal برای مدیریت حالت Access Point
def start_ap_portal(cfg, display=None):
    ssid = 'Ai Clock'
    
    # ۱. بلافاصله صفحه پاک شود و Clock وسط صفحه نمایش داده شود
    if display:
        display.fill(0)
        display.text(ssid, 0, 0, 1)  # 12 برای وسط‌چین شدن کلمه Clock
        display.show()

    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid, authmode=network.AUTH_OPEN)
    
    sta = network.WLAN(network.STA_IF)
    sta.active(False)
    time.sleep(.5)

    print('AP Mode Started:Ai Clock (Open) - IP: 192.168.4.1')

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 80))
    s.listen(2)
    s.setblocking(False)

    ip_shown = False

    while True:
        # ۲. به محض اتصال گوشی به وای‌فای، IP فشرده رسم می‌شود
        if (not ip_shown) and display:
            try:
                st = ap.status('stations')
                if st and len(st) > 0:
                    draw_compact_ip(display, ap.ifconfig()[0])
                    ip_shown = True
            except Exception as e:
                print("Status check error:", e)

        try:
            cl, addr = s.accept()
        except OSError:
            time.sleep_ms(80)
            continue

        try:
            cl.settimeout(2.0)
            req = b''
            while True:
                chunk = cl.recv(1024)
                if not chunk: break
                req += chunk
                if b'\r\n\r\n' in req: break
            
            req_str = req.decode('utf-8', 'ignore')
            lines = req_str.split('\r\n')
            first_line = lines[0] if lines else ''

            if 'POST /save' in first_line:
                content_len = 0
                for line in lines:
                    if line.lower().startswith('content-length:'):
                        content_len = int(line.split(':')[1].strip())
                        break
                
                parts = req_str.split('\r\n\r\n', 1)
                body = parts[1] if len(parts) > 1 else ''
                while len(body) < content_len:
                    more = cl.recv(1024)
                    if not more: break
                    body += more.decode('utf-8', 'ignore')

                form = parse_form_data(body)
                
                cfg['wifi_ssid'] = form.get('wifi_ssid', cfg.get('wifi_ssid', ''))
                cfg['wifi_pass'] = form.get('wifi_pass', '')
                cfg['brightness'] = int(form.get('brightness', 2))
                cfg['fetch_interval'] = int(form.get('fetch_interval', 120))
                
                for key in ('show_date', 'show_usdt', 'show_gold', 'show_btc', 'show_oil', 'show_weather'):
                    cfg[key] = key in form
                    
                save_config(cfg)
                
                # نمایش پیام ذخیره روی ماتریس قبل از ریست
                if display:
                    display.fill(0)
                    display.text("SAVED", 12, 0, 1)
                    display.show()

                resp = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n<html lang="fa" dir="rtl"><body><h2>تنظیمات با موفقیت ذخیره شد!</h2><p>برد تا چند ثانیه دیگر ریستارت می‌شود...</p></body></html>'
                cl.send(resp.encode('utf-8'))
                cl.close()
                time.sleep(1.5)
                machine.reset()
            else:
                html = render_html(cfg)
                resp = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: ' + str(len(html.encode('utf-8'))) + '\r\n\r\n' + html
                cl.send(resp.encode('utf-8'))
                cl.close()
        except Exception as e:
            print("Request handling error:", e)
            try: cl.close()
            except: pass
