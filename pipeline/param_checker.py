def check_missing_params(api_config: dict, params: dict) -> list:
    """
    Kiểm tra các param bắt buộc chưa được cung cấp.
    """
    required = api_config.get("required_params", [])
    missing = [p for p in required if p not in params or params[p] in (None, "")]
    return missing