import json

DEFAULT_CONFIG = {
    "version": 1.0,
    "wifi_ssid": "Redmi14",
    "wifi_pass": "11223345",
    "spi_id": 1,
    "spi_baudrate": 10000000, # این خط اضافه شد
    "pin_sck": 18,
    "pin_mosi": 23,
    "pin_cs": 5,
    "num_matrices": 8,
    "brightness": 2,
    "fetch_interval": 300,
    "show_weather": True,
    "show_usdt": True,
    "show_gold": True,
    "show_btc": True,
    "show_oil": True,
    "show_date": True
}

def load_config():
    cfg = DEFAULT_CONFIG.copy()
    try:
        with open('config.json', 'r') as f:
            user_cfg = json.load(f)
            cfg.update(user_cfg)
    except:
        save_config(cfg)
    return cfg

def save_config(cfg):
    try:
        with open('config.json', 'w') as f:
            json.dump(cfg, f)
        return True
    except:
        return False
