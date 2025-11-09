def ask_user_for_missing(missing: list) -> str:
    """
    Tạo câu hỏi gợi ý nếu thiếu tham số.
    """
    prompts = {
        "branch_name": "Bạn muốn xem chi nhánh nào?",
        "start_date": "Khoảng thời gian bắt đầu là khi nào?",
        "end_date": "Khoảng thời gian kết thúc là khi nào?",
        "month": "Tháng nào bạn muốn xem?",
        "year": "Năm nào bạn muốn xem?"
    }

    missing_questions = [prompts.get(m, f"Thiếu tham số {m}") for m in missing]
    return "Xin bổ sung: " + ", ".join(missing_questions)


def reply_user(api_response: dict, api_config: dict) -> str:
    """
    Tạo phản hồi tự nhiên cho người dùng từ API response dựa trên luật trong api_config.
    """
    print('dung')
    print(api_response)
    
    if not isinstance(api_response, dict):
        return "Tôi chưa hiểu rõ kết quả từ API."

    result = api_response.get("result")
    if not result:
        return "API không trả về dữ liệu."

    # Lấy field theo config
    result_field = api_config.get("result_field")
    print(result_field)
    
    if result_field and result_field in result:
        value = result[result_field]
        if value is not None:
            return str(value)

    # Fallback: xử lý theo kiểu dữ liệu
    if isinstance(result, (int, float)):
        # return f"✅ Kết quả là: {result:,} VND."
        return result
    elif isinstance(result, dict):
        items = []
        for k, v in result.items():
            if isinstance(v, (int, float)):
                items.append(f"{k}: {v:,} VND")
            else:
                items.append(f"{k}: {v}")
        return "📊 Chi tiết:\n" + "\n".join(items)
    elif isinstance(result, list):
        return "🏢 Danh sách:\n- " + "\n- ".join(map(str, result))

    return "Tôi chưa hiểu rõ kết quả từ API."
    
# bot_capabilities.py
def get_bot_capabilities():
    """
    Trả về năng lực mà bot có thể hỗ trợ người dùng.
    """
    capabilities = {
        "Doanh_Thu": "Tra cứu doanh thu theo ngày, tháng, quý, năm hoặc theo chi nhánh.",
        "Chi_Phí": "Theo dõi chi phí vận hành, chi phí marketing, nhân sự, ...",
        "Lợi_Nhuận": "Tính toán lợi nhuận gộp hoặc ròng theo kỳ.",
        "Kpi": "Theo dõi KPI nhân viên, bộ phận, hoặc toàn công ty.",
        "Khách_Hàng": "Thống kê số lượng khách hàng mới, quay lại, hoặc theo phân khúc.",
        "So_Sánh": "So sánh hiệu suất giữa các kỳ hoặc giữa các chi nhánh.",
        "Dự_Báo": "Dự báo doanh thu hoặc chi phí dựa trên dữ liệu lịch sử."
    }

    intro = (
        "Xin chào! Tôi là trợ lý phân tích dữ liệu kinh doanh. "
        "Tôi có thể giúp bạn tra cứu nhanh các thông tin như:\n"
    )
    
    for key, desc in capabilities.items():
        intro += f"• {key.replace('_', ' ').title()}: {desc}\n"

    outro = (
        "\nBạn có thể hỏi ví dụ như:\n"
        "› Doanh thu quý 3 năm nay của chi nhánh Hà Nội là bao nhiêu?\n"
        "› So sánh chi phí marketing tháng 10 và tháng 11.\n"
        "› KPI trung bình của nhân viên chi nhánh Thái Hà tháng này."
    )

    return intro + outro

def chatgpt_fallback(user_query: str):
    """
    Fallback sang ChatGPT nếu câu hỏi nằm ngoài phạm vi định nghĩa
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là trợ lý ảo thông minh, hỗ trợ người dùng về dữ liệu doanh nghiệp và câu hỏi chung."},
            {"role": "user", "content": user_query}
        ],
        max_tokens=200,
        temperature=0.6
    )
    return response["choices"][0]["message"]["content"]