import os
import gc
import machine
import urequests
from config import save_config

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/AJAVADI/Clock/main/"
HEADERS = {"User-Agent": "ESP32-MicroPython"}

def draw_progress(display, progress_ratio):
    """رسم نوار پیشرفت پیکسلی در ردیف آخر ماتریس"""
    if not display:
        return
    display.fill(0)
    display.text("OTA", 20, 0, 1)
    
    max_w = getattr(display, 'width', 64)
    bar_w = int(max_w * progress_ratio)
    
    for x in range(bar_w):
        display.pixel(x, 7, 1)
    display.show()

def check_and_update(cfg, display=None):
    """بررسی و اعمال خودکار آپدیت از گیت‌هاب"""
    gc.collect()
    local_version = cfg.get("version", 1.0)
    print("Checking OTA updates... Local version:", local_version)

    # 1. دانلود متادیتا نسخه
    meta_url = GITHUB_RAW_BASE + "version.json"
    res = None
    try:
        res = urequests.get(meta_url, headers=HEADERS)
        if res.status_code != 200:
            print("OTA: version.json not found (HTTP {})".format(res.status_code))
            res.close()
            return
        meta = res.json()
        res.close()
    except Exception as e:
        print("OTA Check failed:", e)
        if res:
            res.close()
        return

    remote_version = meta.get("version", local_version)
    files_to_update = meta.get("files", [])

    if remote_version <= local_version or not files_to_update:
        print("OTA: System is up to date.")
        return

    print("New version found: {}. Starting update...".format(remote_version))

    # 2. دانلود استریمی فایل‌ها تکه‌تکه (جلوگیری از پر شدن رم و قفل سوکت)
    total_files = len(files_to_update)
    for idx, filename in enumerate(files_to_update):
        draw_progress(display, idx / total_files)
        
        file_url = GITHUB_RAW_BASE + filename
        tmp_filename = filename + ".tmp"
        
        print("Downloading {}...".format(filename))
        res = None
        try:
            gc.collect()
            res = urequests.get(file_url, headers=HEADERS)
            if res.status_code == 200:
                with open(tmp_filename, "wb") as f:
                    while True:
                        chunk = res.raw.read(512)
                        if not chunk:
                            break
                        f.write(chunk)
                res.close()
            else:
                print("Failed to download {}, HTTP {}".format(filename, res.status_code))
                res.close()
                return
        except Exception as e:
            print("Download error {}: {}".format(filename, e))
            if res:
                res.close()
            return

    # 3. جایگزینی امن فایل‌ها
    draw_progress(display, 1.0)
    print("Applying updates...")
    for filename in files_to_update:
        tmp_filename = filename + ".tmp"
        try:
            os.remove(filename)
        except OSError:
            pass
        os.rename(tmp_filename, filename)

    # 4. آپدیت نسخه در کانفیگ و ریبوت برد
    cfg["version"] = remote_version
    save_config(cfg)
    print("Update complete! Rebooting...")
    
    if display:
        display.fill(0)
        display.text("DONE", 16, 0, 1)
        display.show()
    
    machine.reset()

