def ask_user_for_missing(missing: list) -> str:
    """
    Tạo câu hỏi gợi ý nếu thiếu tham số.
    """
    prompts = {
        "branch_name": "Bạn muốn xem chi nhánh nào?",
        "revenue_start_date": "Khoảng thời gian bắt đầu là khi nào?",
        "revenue_end_date": "Khoảng thời gian kết thúc là khi nào?",
        "month": "Tháng nào bạn muốn xem?",
        "year": "Năm nào bạn muốn xem?"
    }

    missing_questions = [prompts.get(m, f"Thiếu tham số {m}") for m in missing]
    return "Xin bổ sung: " + ", ".join(missing_questions)


def reply_user(result) -> str:
    """
    Tạo phản hồi tự nhiên cho người dùng.
    """
    if isinstance(result, (int, float)):
        return f"✅ Doanh thu là khoảng {result:,} VND."
    elif isinstance(result, dict):
        items = [f"{k}: {v:,} VND" for k, v in result.items()]
        return "📊 Chi tiết doanh thu:\n" + "\n".join(items)
    elif isinstance(result, list):
        return "🏢 Top chi nhánh có doanh thu cao nhất:\n- " + "\n- ".join(result)
    else:
        return "Tôi chưa hiểu rõ kết quả từ API."
    
# bot_capabilities.py
def get_bot_capabilities():
    """
    Trả về năng lực mà bot có thể hỗ trợ người dùng.
    """
    capabilities = {
        "doanh_thu": "Tra cứu doanh thu theo ngày, tháng, quý, năm hoặc theo chi nhánh.",
        "chi_phi": "Theo dõi chi phí vận hành, chi phí marketing, nhân sự, ...",
        "loi_nhuan": "Tính toán lợi nhuận gộp hoặc ròng theo kỳ.",
        "kpi": "Theo dõi KPI nhân viên, bộ phận, hoặc toàn công ty.",
        "khach_hang": "Thống kê số lượng khách hàng mới, quay lại, hoặc theo phân khúc.",
        "so_sanh": "So sánh hiệu suất giữa các kỳ hoặc giữa các chi nhánh.",
        "du_bao": "Dự báo doanh thu hoặc chi phí dựa trên dữ liệu lịch sử."
    }

    intro = (
        "Xin chào 👋 Tôi là trợ lý phân tích dữ liệu kinh doanh. "
        "Tôi có thể giúp bạn tra cứu nhanh các thông tin như:\n"
    )
    
    for key, desc in capabilities.items():
        intro += f"• **{key.replace('_', ' ').title()}**: {desc}\n"

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