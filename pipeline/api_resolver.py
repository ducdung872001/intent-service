import json
import os

BASE_DIR = os.path.dirname(__file__)
API_REGISTRY_PATH = os.path.join(BASE_DIR, "config", "api_registry.json")
SERVICE_HOSTS_PATH = os.path.join(BASE_DIR, "config", "service_hosts.json")

_cache = {}

def load_json(path):
    if path in _cache:
        return _cache[path]
    with open(path, "r", encoding="utf-8") as f:
        _cache[path] = json.load(f)
    return _cache[path]


def api_resolver(intent: str):
    """Ánh xạ intent sang API endpoint đầy đủ (gồm hostname)."""
    registry = load_json(API_REGISTRY_PATH)
    hosts = load_json(SERVICE_HOSTS_PATH)

    # Nếu intent chưa được khai báo trong registry thì phản hồi lại người dùng về năng lực của bot (Hỏi về Doanh thu | ...)
    # thì sửa lại code dưới như nào (thay thế cho báo lỗi)
    api_info = registry.get(intent)
    if not api_info:
        # raise ValueError(f"Intent '{intent}' chưa được khai báo trong {API_REGISTRY_PATH}")
        return ""

    service = api_info.get("service")
    hostname = hosts.get(service)
    if not hostname:
        # raise ValueError(f"Service '{service}' chưa có hostname trong {SERVICE_HOSTS_PATH}")
        return ""

    full_url = f"{hostname.rstrip('/')}/{api_info['endpoint'].lstrip('/')}"
    api_info["url"] = full_url
    return api_info