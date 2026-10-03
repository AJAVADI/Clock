import time
from machine import Pin, SPI
from config import load_config
from fc16 import FC16Matrix
from network_time import connect_wifi, sync_ntp, gregorian_to_jalali
from api_data import fetch_weather, fetch_usdt, fetch_gold, fetch_btc, fetch_oil
import web_server
import ota



cfg = load_config()

spi = SPI(cfg['spi_id'], baudrate=cfg['spi_baudrate'], polarity=0, phase=0,
          sck=Pin(cfg['pin_sck']), mosi=Pin(cfg['pin_mosi']))
cs = Pin(cfg['pin_cs'], Pin.OUT)
display = FC16Matrix(spi, cs, cfg['num_matrices'])
display.brightness(cfg['brightness'])

def show_status(text):
    display.fill(0)
    display.text(text[:8], 0, 0, 1)
    display.show()

def scroll_text(text, delay_ms=35, pause_at_end_ms=5000):
    text_len = len(text) * 8
    target_stop_x = display.width - text_len  # نقطه‌ای که آخرین کاراکتر به لبه راست (پیکسل 63) می‌چسبد
    
    for x in range(display.width, -text_len, -1):
        display.fill(0)
        display.text(text, x, 0, 1)
        display.show()
        
        # اگر به انتهای متن رسیدیم و مکث تعریف شده بود
        if pause_at_end_ms > 0 and x == target_stop_x:
            time.sleep_ms(pause_at_end_ms)
            
        time.sleep_ms(delay_ms)
        
        
connected = connect_wifi(cfg['wifi_ssid'], cfg['wifi_pass'], show_status, timeout=10)
if not connected:
    #show_status('AP')
    web_server.start_ap_portal(cfg, display)

#sync_ntp(show_status)
    
# تلاش اولیه برای همگام‌سازی ساعت / تست اینترنت
if not sync_ntp(show_status):
    net_ok = False
    
    # تا ۱۰ بار و هر بار ۱ دقیقه تلاش مجدد (مجموعاً ۱۰ دقیقه)
    for _ in range(1):
        t_end = time.ticks_add(time.ticks_ms(), 60_000)
        while time.ticks_diff(t_end, time.ticks_ms()) > 0:
            scroll_text(" net !!! ", delay_ms=35, pause_at_end_ms=0)
            
        # بعد از هر ۱ دقیقه اسکرول، دوباره اینترنت/NTP تست می‌شود
        if sync_ntp(show_status):
            net_ok = True
            break
            
    # اگر بعد از ۱۰ دقیقه وصل نشد، می‌رود به حالت تنظیمات
    if not net_ok:
        web_server.start_ap_portal(cfg, display)
    
ota.check_and_update(cfg, display)

last_fetch = 0
cached_temp = '--C'
cached_usdt = 'USDT:--'
cached_gold = 'GOLD:--'
cached_btc = 'BTC:--'
cached_oil = 'OIL:--'

while True:
    now = time.time()
    if now - last_fetch > cfg['fetch_interval'] or last_fetch == 0:
        if cfg.get('show_weather', True): cached_temp = fetch_weather()
        if cfg.get('show_usdt', True): cached_usdt = fetch_usdt()
        if cfg.get('show_gold', True): cached_gold = fetch_gold()
        if cfg.get('show_btc', True): cached_btc = fetch_btc()
        if cfg.get('show_oil', True): cached_oil = fetch_oil()
        last_fetch = now

    # نمایش ساعت و دما به مدت ۶ ثانیه روی نمایشگر
    start_clock = time.time()
    while time.time() - start_clock < 6:
        tehran_epoch = time.time() + (3 * 3600 + 30 * 60)
        tm = time.localtime(tehran_epoch)
        display.fill(0)

        # ۱. ساعت و دقیقه
        display.text(f'{tm[3]:02d}', 0, 0, 1)
        display.text(f'{tm[4]:02d}', 20, 0, 1)

        # ۲. دو نقطه چشمک‌زن باریک
        #if int(time.time() * 2) % 2 == 0:
        if int(time.ticks_ms() % 1000) < 500: 
            # نقطه بالا (۲x۲)
            display.pixel(17, 1, 1)
            display.pixel(18, 1, 1)
            display.pixel(17, 2, 1)
            display.pixel(18, 2, 1)

            # نقطه پایین (۲x۲)
            display.pixel(17, 4, 1)
            display.pixel(18, 4, 1)
            display.pixel(17, 5, 1)
            display.pixel(18, 5, 1)

             # ۳. دمای عددی + علامت درجه ۳x۳ با سوراخ وسط
        if cfg.get('show_weather', True) and cached_temp != '--C':
            temp_num = cached_temp.replace('C', '')
            display.text(temp_num, 42, 0, 1)
            
            # ردیف بالا (y=0)
            #display.pixel(59, 0, 1);
            display.pixel(60, 0, 1)#; display.pixel(61, 0, 1)
            # ردیف وسط (y=1) با سوراخ خالی در x=60
            display.pixel(59, 1, 1); display.pixel(61, 1, 1)
            # ردیف پایین (y=2)
            #display.pixel(59, 2, 1);
            display.pixel(60, 2, 1)#; display.pixel(61, 2, 1)

        display.show()
        time.sleep_ms(100)

    if cfg.get('show_date', True):
        tehran_epoch = time.time() + (3 * 3600 + 30 * 60)
        tm = time.localtime(tehran_epoch)
        jy, jm, jd = gregorian_to_jalali(tm[0], tm[1], tm[2])
        scroll_text(f'{jy}/{jm:02d}/{jd:02d}')

    if cfg.get('show_usdt', True): scroll_text(cached_usdt)
    if cfg.get('show_gold', True): scroll_text(cached_gold)
    if cfg.get('show_btc', True): scroll_text(cached_btc)
    if cfg.get('show_oil', True): scroll_text(cached_oil)
    
        # تبریک تولد - ۵ بار اسکرول متوالی
  #  for _ in range(8):
  #      scroll_text("Happy Birth Day SOMAYE ", delay_ms=35, pause_at_end_ms=4000)

