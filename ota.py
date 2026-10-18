import urequests
import os
import machine
from config import load_config, save_config

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/AJAVADI/Clock/main/"
HEADERS = {"User-Agent": "ESP32-MicroPython"}

def draw_progress(display, ratio):
    if not display:
        return
    display.fill(0)
    total_cols = 64
    active_cols = int(ratio * total_cols)
    if active_cols > total_cols:
        active_cols = total_cols
    for col in range(active_cols):
        for row in range(2, 6):
            display.pixel(col, row, 1)
    display.show()

def cleanup_tmp_files():
    """حذف تمام فایل‌های موقت .tmp برای جلوگیری از پر شدن حافظه فلش"""
    try:
        for fname in os.listdir():
            if fname.endswith(".tmp"):
                try:
                    os.remove(fname)
                    print(f"Cleaned up orphan tmp: {fname}")
                except OSError:
                    pass
    except Exception as e:
        print(f"Error during tmp cleanup: {e}")

def check_for_updates(display=None):
    # تمیزکاری اولیه فایل‌های احتمالی باقی‌مانده از دفعات قبل
    cleanup_tmp_files()

    cfg = load_config()
    local_version = cfg.get("version", 1.0)
    print(f"Checking for updates... (Current version: {local_version})")

    try:
        res = urequests.get(GITHUB_RAW_BASE + "version.json", headers=HEADERS)
        if res.status_code != 200:
            print("Update check failed, HTTP", res.status_code)
            res.close()
            return
        meta = res.json()
        res.close()
    except Exception as e:
        print("Update check error:", e)
        return

    remote_version = meta.get("version", local_version)
    files_to_update = meta.get("files", [])

    if remote_version <= local_version or not files_to_update:
        print("System is up to date.")
        return

    print(f"New version found: {remote_version}. Files: {files_to_update}")

    total_files = len(files_to_update)
    for idx, filename in enumerate(files_to_update):
        file_url = GITHUB_RAW_BASE + filename
        tmp_filename = filename + ".tmp"
        print(f"Downloading {filename}...")

        res = None
        try:
            res = urequests.get(file_url, headers=HEADERS)
            if res.status_code == 200:
                with open(tmp_filename, "wb") as f:
                    while True:
                        chunk = res.raw.read(256)
                        if not chunk:
                            break
                        f.write(chunk)
                res.close()
                progress = (idx + 1) / total_files
                draw_progress(display, progress)
            else:
                print(f"Failed to download {filename}, HTTP {res.status_code}")
                res.close()
                cleanup_tmp_files()
                return
        except Exception as e:
            print(f"Download error {filename}: {e}")
            if res:
                try:
                    res.close()
                except:
                    pass
            cleanup_tmp_files()
            return

    # جایگزینی امن فایل‌ها
    draw_progress(display, 1.0)
    print("Applying updates...")
    for filename in files_to_update:
        tmp_filename = filename + ".tmp"
        try:
            os.remove(filename)
        except OSError:
            pass
        os.rename(tmp_filename, filename)

    # پاکسازی نهایی اطمینان‌بخش
    cleanup_tmp_files()

    # آپدیت نسخه در کانفیگ و ریبوت برد
    cfg["version"] = remote_version
    save_config(cfg)
    print("Update complete! Rebooting...")

    if display:
        display.fill(0)
        display.text("DONE", 16, 0, 1)
        display.show()

    machine.reset()
