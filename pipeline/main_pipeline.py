# pipeline/main_pipeline.py
from pipeline.intent_detector import detect_intent, extract_intent_and_entities
from pipeline.api_resolver import api_resolver
from pipeline.parameter_extractor import extract_parameters
from pipeline.param_checker import check_missing_params
from pipeline.api_caller import call_api
from pipeline.dialogue_manager import ask_user_for_missing, reply_user


def run_pipeline(user_query: str):
    """
    Pipeline chính: từ câu hỏi user → gọi API → trả kết quả
    """
    print(f"[User query] {user_query}")

    # B1. Xác định intent
    intent_and_params = extract_intent_and_entities(user_query)
    # intent = detect_intent(user_query)
    intent = intent_and_params.get("intent")
    print(f"[Intent] {intent}")

    # B2. Lấy cấu hình API
    api_config = api_resolver(intent)
    print(f"[API config] {api_config['url']}")

    # B3. Trích tham số
    # params = extract_parameters(user_query, api_config)
    params = intent_and_params.get("entities");
    print(f"[Parameters] {params}")

    # B4. Kiểm tra thiếu
    missing = check_missing_params(api_config, params)
    if missing:
        return ask_user_for_missing(missing)

    # B5. Gọi API
    result = call_api(api_config, params)

    # B6. Trả lời user
    return reply_user(result)