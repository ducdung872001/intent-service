# pipeline/main_pipeline.py
from pipeline.intent_detector import detect_intent, extract_intent_and_entities, chatgpt_fallback
from pipeline.api_resolver import api_resolver
from pipeline.parameter_extractor import extract_parameters
from pipeline.param_checker import check_missing_params
from pipeline.api_caller import call_api
from pipeline.dialogue_manager import ask_user_for_missing, reply_user, get_bot_capabilities

# Biến nhớ context (tạm, bạn có thể thay bằng redis hoặc session id)
conversation_context = {}

def run_pipeline(user_query: str, session_id: str = "default", token: str = None):
    print(f"[User query] {user_query}")

    # === Lấy hoặc khởi tạo context ===
    context = conversation_context.get(session_id, {"intent": None, "entities": {}})

    # === Phân tích intent và entity từ câu hỏi mới ===
    intent_and_params = extract_intent_and_entities(user_query)
    detected_intent = intent_and_params.get("intent")
    detected_entities = intent_and_params.get("entities", {})

    print(f"👉 Detected intent: {detected_intent}")
    print(f"👉 Context intent: {context.get('intent')}")

    # === Quy tắc xác định intent ===
    if context.get("intent") and detected_intent and detected_intent != context["intent"]:
        # So sánh xem user có đang hỏi ý định khác hẳn không
        # Nếu câu chứa từ khóa "doanh thu", "chi phí", "so sánh" ... khác intent cũ -> reset
        if any(kw in user_query.lower() for kw in ["doanh thu", "chi phí", "so sánh", "thống kê", "tổng hợp"]):
            print("🔄 Intent thực sự khác, reset context.")
            context = {"intent": detected_intent, "entities": {}}
        else:
            # Nếu không có dấu hiệu hỏi mới -> coi là bổ sung entity
            print("➕ Chỉ bổ sung thông tin, giữ intent cũ.")
            detected_intent = context["intent"]

    elif not detected_intent:
        # Nếu AI không phát hiện intent -> dùng intent trước
        detected_intent = context.get("intent")

    # Nếu vẫn không có intent nào xác định được
    if not detected_intent:
        return chatgpt_fallback(user_query)

    # === Cập nhật intent và entity vào context ===
    context["intent"] = detected_intent
    if detected_entities:
        # Chỉ update các entity có giá trị thực (loại bỏ None hoặc "")
        context["entities"].update({k: v for k, v in detected_entities.items() if v})

    print(f"[🧠 Context sau merge] {context['entities']}")

    # === Lấy config và kiểm tra tham số ===
    api_config = api_resolver(detected_intent)
    if not api_config:
        return chatgpt_fallback(user_query)

    missing = check_missing_params(api_config, context["entities"])
    if missing:
        conversation_context[session_id] = context
        return ask_user_for_missing(missing)

    # === Đủ tham số => gọi API ===
    result = call_api(api_config, context["entities"], token=token)    
    
    conversation_context.pop(session_id, None)
    return reply_user(result, api_config=api_config)