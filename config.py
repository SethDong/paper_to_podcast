import os
import json
from pathlib import Path

CONFIG_FILE = "config.json"

def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"api_key": ""}

def save_config(config):
    """保存配置文件"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def get_api_key():
    """获取API密钥"""
    config = load_config()
    return config.get("api_key", "")

def set_api_key(api_key):
    """设置API密钥"""
    config = load_config()
    config["api_key"] = api_key
    save_config(config) 

def get_fish_api_key():
    """获取API密钥"""
    config = load_config()
    return config.get("fish_api_key", "")

def set_fish_api_key(api_key):
    """设置API密钥"""
    config = load_config()
    config["fish_api_key"] = api_key
    save_config(config)     
