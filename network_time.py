import network, time, ntptime

print("Connect To WiFi...")

def connect_wifi(ssid, password, show_status=None, timeout=15, device_name="AiClock"):
    if show_status:
        show_status("WIFI")
    time.sleep(3)

    import __main__
    display = getattr(__main__, 'display', None)
    if display:
        display.fill(0)
        display.pixel(28, 7, 1)
        display.pixel(32, 7, 1)
        display.pixel(36, 7, 1)
        display.show()

    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    time.sleep(0.5)
    wlan.active(True)
    
    # تنظیم نام دیوایس در شبکه قبل از اتصال
    try:
        network.hostname(device_name)
    except AttributeError:
        try:
            wlan.config(dhcp_hostname=device_name)
        except Exception:
            pass

    if wlan.isconnected():
        wlan.disconnect()
        time.sleep(0.5)

    clean_ssid = str(ssid).strip()
    clean_pass = str(password).strip()

    wlan.connect(clean_ssid, clean_pass)

    start = time.time()
    while not wlan.isconnected():
        status = wlan.status()
        
        if time.time() - start > timeout:
            return False
        time.sleep(1)

    return True

def sync_ntp(show_status_cb=None):
    if show_status_cb:
        show_status_cb("NTP")
    try:
        ntptime.host = 'pool.ntp.org'
        ntptime.settime()
        return True
    except Exception:
        return False

def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621
    gy2 = gy if gm > 2 else gy - 1
    days = (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) - 80 + gd + g_d_m[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd
