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
    # رسم کلمه OTA با یک پیکسل شیفت به بالا تا ردیف 7 باز بماند
    display.text("OTA", 20, -1, 1)
    
    max_w = getattr(display, 'width', 64)
    # حداقل یک پیکسل یا به اندازه نسبت دانلود
    bar_w = int(max_w * max(0.0, min(1.0, progress_ratio)))
    
    # رسم نوار پیشرفت روی ردیف 7 (خط کف)
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

    # 2. دانلود استریمی فایل‌ها تکه‌تکه و رسم پیشرفت بر اساس حجم دریافت شده
    total_files = len(files_to_update)
    for idx, filename in enumerate(files_to_update):
        file_url = GITHUB_RAW_BASE + filename
        tmp_filename = filename + ".tmp"
        
        print("Downloading {}...".format(filename))
        res = None
        try:
            gc.collect()
            res = urequests.get(file_url, headers=HEADERS)
            if res.status_code == 200:
                # خواندن طول فایل از هدر سرور در صورت وجود
                content_len_hdr = res.headers.get("Content-Length")
                total_len = int(content_len_hdr) if content_len_hdr else 4096
                downloaded = 0
                
                with open(tmp_filename, "wb") as f:
                    while True:
                        chunk = res.raw.read(256)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # محاسبه نسبت کل پیشرفت با احتساب تعداد کل فایل‌ها
                        file_progress = downloaded / total_len
                        overall_progress = (idx + min(1.0, file_progress)) / total_files
                        draw_progress(display, overall_progress)
                        
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
