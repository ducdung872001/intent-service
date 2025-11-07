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