def check_missing_params(api_config, params):
    missing = []

    # Kiểm tra các required params thông thường
    for p in api_config.get("required_params", []):
        if p not in params or not params[p]:
            missing.append(p)

    # Kiểm tra nhóm "ít nhất một"
    at_least_one = api_config.get("at_least_one", [])
    if at_least_one:
        if not any(params.get(p) for p in at_least_one):
            missing.append(f"Ít nhất một trong {at_least_one} phải được cung cấp")

    return missing