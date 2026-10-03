import sys
import time
from machine import Pin

print("Press Boot if Stop")
time.sleep(2)

# پین دکمه BOOT (GPIO 0)
boot_btn = Pin(0, Pin.IN, Pin.PULL_UP)

# اگر موقع اتصال برق یا ریست سخت‌افزاری دکمه را نگه داشته باشی
if boot_btn.value() == 0:
    #print("\n[!] SAFE MODE: BOOT button held at startup! Execution halted.")
    print("STOPED...")
    #sys.exit()
    while True:
        time.sleep(1) 
        print(".")

print("NO STOPED")
