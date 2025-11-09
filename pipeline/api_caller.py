import random
import time
import requests
import shlex

def print_curl(api_config: dict, params: dict, token: str = None):
    method = api_config.get("method", "GET").upper()
    url = api_config["url"]
    headers = api_config.get("headers", {}).copy()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    curl_cmd = ["curl"]

    # Method
    if method != "GET":
        curl_cmd += ["-X", method]

    # Headers
    for k, v in headers.items():
        curl_cmd += ["-H", f"{k}: {v}"]

    # Data
    if method == "POST":
        import json
        curl_cmd += ["-d", json.dumps(params)]

    # URL and params
    if method == "GET" and params:
        from urllib.parse import urlencode
        url += "?" + urlencode(params)
    curl_cmd += [url]

    # Join as a string for printing
    print("Generated curl command:")
    print(" ".join(shlex.quote(x) for x in curl_cmd))

def call_api(api_config: dict, params: dict, token: str = None):
    # In curl trước khi gọi
    print_curl(api_config, params, token)

    method = api_config.get("method", "GET").upper()
    url = api_config["url"]
    headers = api_config.get("headers", {}).copy()
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    response_type = api_config.get("response_type")

    try:
        if method == "GET":
            response = requests.get(url, params=params, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=params, headers=headers, timeout=10)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        data = response.json()
        print('data:', data)

        if response_type == "scalar":
            return data
        elif response_type in ("object", "list"):
            return data
        else:
            return data

    except requests.exceptions.RequestException as e:
        print(f"[Error] API call failed: {e}")
        return None
