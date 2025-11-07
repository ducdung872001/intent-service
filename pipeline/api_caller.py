import random
import time

def call_api(api_config: dict, params: dict):
    """
    Mô phỏng gọi API. Thực tế có thể dùng requests.get/post.
    """
    print(f"[Mock API Call] {api_config['method']} {api_config['url']} with {params}")
    time.sleep(0.5)  # giả lập độ trễ
    if api_config["response_type"] == "scalar":
        return random.randint(100_000_000, 500_000_000)
    elif api_config["response_type"] == "object":
        return {"2025-07": 120_000_000, "2025-08": 180_000_000, "2025-09": 160_000_000}
    elif api_config["response_type"] == "list":
        return ["Hà Nội", "Hải Phòng", "Đà Nẵng"]
    return None