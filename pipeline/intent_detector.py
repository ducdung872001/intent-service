import os
import json
import re
from datetime import datetime, timedelta
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ====== Đọc schema doanh thu ======
with open("schemas/revenue_schema.json", "r", encoding="utf-8") as f:    
    schema_data = json.load(f)

# ====== Response schema ======
response_schemas = [
    ResponseSchema(
        name="intent",
        description=(
            "Ý định của người dùng. Có thể là một trong các loại sau:\n"
            "- get_capacity: người dùng hỏi về năng lực của bot/khả năng của bot làm được những gì.\n"
            "- get_revenue_by_customer: lấy doanh thu theo khách hàng.\n"
            "- get_revenue_by_contract: lấy doanh thu theo hợp đồng.\n"
            "- get_debt_by_customer: lấy số tiền khách hàng còn nợ, lấy công nợ của khách hàng.\n"
            "- get_debt_by_contract: lấy số tiền hợp đồng còn nợ, lấy công nợ của hợp đồng.\n"            
            "Nếu không chắc chắn, chọn intent gần nhất có thể."
        )
    ),
    ResponseSchema(
        name="entities",
        description=f"Các trường liên quan đến {schema_data['name']}, bao gồm: {', '.join(f['name'] for f in schema_data['fields'])}"
    )
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions()

# ====== Prompt ======
prompt = ChatPromptTemplate.from_template("""
Bạn là AI hỗ trợ hiểu truy vấn người dùng bằng tiếng Việt.

Truy vấn: {query}

{format_instructions}

Yêu cầu:
- Xác định intent chính xác nhất dựa vào loại thông tin mà người dùng muốn truy vấn.
- Nếu người dùng đề cập tới 'hợp đồng', 'khách hàng', 'chi nhánh', ... hãy phân loại intent tương ứng.
- Chỉ trích xuất intent và entities theo schema.
- Không tính toán ngày, không giải thích gì.
- Nếu trong query có từ khóa thời gian, chỉ trả nguyên từ khóa trong entities (ví dụ 'hôm nay', 'tuần trước', ...).
- Luôn trả JSON hợp lệ.
""")

chain = LLMChain(
    llm=llm,
    prompt=prompt,
    output_parser=output_parser
)

def detect_intent(user_query: str) -> str:
    result = extract_intent_and_entities(user_query)    
    result = result.get("intent")    
    return result

# ====== Xử lý từ khóa thời gian và tính revenue_start_date / revenue_end_date ======
def compute_revenue_dates(time_keyword: str, current_date: datetime):
    today = current_date
    keyword = (time_keyword or "").lower()

    if keyword in ["hôm nay", "ngày hôm nay"]:
        return today, today
    elif keyword in ["hôm qua", "ngày hôm qua", "hôm trước", "ngày hôm trước"]:
        yesterday = today - timedelta(days=1)
        return yesterday, yesterday
    elif keyword in ["ngày mai", "ngày hôm sau"]:
        tomorrow = today + timedelta(days=1)
        return tomorrow, tomorrow
    elif keyword in ["ngày kia"]:
        return today + timedelta(days=2), today + timedelta(days=2)
    
    # ---- X ngày gần đây ----
    recent_match = re.match(r"(\d+)\s+ngày gần đây", keyword)
    if recent_match:
        days = int(recent_match.group(1))
        start_date = today - timedelta(days=days-1)  # bao gồm hôm nay
        return start_date, today
    elif keyword == "tuần này":
        # Tuần bắt đầu Chủ nhật
        start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)
        return start_of_week, today
    elif keyword == "tuần trước":
        start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)
        revenue_start_date = start_of_week - timedelta(days=7)
        revenue_end_date = start_of_week - timedelta(days=1)
        return revenue_start_date, revenue_end_date
    elif keyword == "tuần sau":
        # Chủ nhật tuần hiện tại
        start_of_current_week = today - timedelta(days=(today.weekday() + 1) % 7)
        revenue_start_date = start_of_current_week + timedelta(days=7)  # Chủ nhật tuần sau
        revenue_end_date = start_of_current_week + timedelta(days=13)   # Thứ Bảy tuần sau
        return revenue_start_date, revenue_end_date
    
    week_of_month_match = re.search(r"tuần thứ (\d+) trong tháng", keyword)
    if week_of_month_match:
        n = int(week_of_month_match.group(1))
        first_day_of_month = today.replace(day=1)
        # Chủ nhật đầu tiên trong tháng
        first_sunday = first_day_of_month + timedelta(days=(6 - first_day_of_month.weekday()) % 7)
        revenue_start_date = first_sunday + timedelta(weeks=n-1)
        revenue_end_date = revenue_start_date + timedelta(days=6)
        return revenue_start_date, revenue_end_date

    elif keyword in ["tháng này", "tháng hiện tại"]:
        start_of_month = today.replace(day=1)
        return start_of_month, today
    elif keyword in ["tháng trước", "tháng rồi"]:
        # Xác định tháng trước
        if today.month == 1:
            prev_month = 12
            year = today.year - 1
        else:
            prev_month = today.month - 1
            year = today.year
        start_of_prev_month = datetime(year, prev_month, 1)
        # Ngày cuối của tháng trước
        if prev_month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, prev_month + 1, 1)
        end_of_prev_month = next_month - timedelta(days=1)
        return start_of_prev_month, end_of_prev_month
    elif keyword == "năm nay":
        start_of_year = today.replace(month=1, day=1)
        return start_of_year, today
    elif keyword == "năm trước":
        start_of_last_year = datetime(today.year - 1, 1, 1)
        end_of_last_year = datetime(today.year - 1, 12, 31)
        return start_of_last_year, end_of_last_year
    
    week_of_year_match = re.search(r"tuần thứ (\d+) trong năm", keyword)
    if week_of_year_match:
        n = int(week_of_year_match.group(1))
        first_day_of_year = today.replace(month=1, day=1)
        first_sunday = first_day_of_year + timedelta(days=(6 - first_day_of_year.weekday()) % 7)
        revenue_start_date = first_sunday + timedelta(weeks=n-1)
        revenue_end_date = revenue_start_date + timedelta(days=6)
        return revenue_start_date, revenue_end_date
    
    # ---- Quý ----
    quarter_match = re.search(
        r"quý\s+((?:i{1,3}|iv)|[1-4])\s+năm\s+(nay|trước)",
        keyword,
        flags=re.IGNORECASE
    )
    if quarter_match:
        q, year_ref = quarter_match.groups()
        # Chuyển La Mã sang số
        roman_to_int = {"i":1, "ii":2, "iii":3, "iv":4}
        q_num = roman_to_int.get(q.lower(), None)
        if not q_num:
            q_num = int(q)
        # Xác định năm
        year = today.year if year_ref == "nay" else today.year - 1
        # Xác định ngày đầu và cuối quý
        month_starts = [1,4,7,10]
        start_month = month_starts[q_num-1]
        start_date = datetime(year=year, month=start_month, day=1)
        if q_num < 4:
            end_month = month_starts[q_num] - 1
            end_day = (datetime(year, end_month+1,1) - timedelta(days=1)).day
        else:
            end_month = 12
            end_day = 31
        end_date = datetime(year=year, month=end_month, day=end_day)
        return start_date, end_date
    
     # 6. Khoảng cụ thể: từ dd/mm/yyyy đến dd/mm/yyyy
    match = re.search(r"từ (\d{2}/\d{2}/\d{4}) đến (\d{2}/\d{2}/\d{4})", keyword)
    if match:
        start_str, end_str = match.groups()
        revenue_start_date = datetime.strptime(start_str, "%d/%m/%Y")
        revenue_end_date = datetime.strptime(end_str, "%d/%m/%Y")
        return revenue_start_date, revenue_end_date

    # 7. Mặc định: hôm nay
    return today, today

# ====== Hàm chính ======
def extract_intent_and_entities(query: str):
    now = datetime.now()

    # ❌ Không cho AI tính ngày, chỉ trích entities
    result = chain.invoke({"query": query, "format_instructions": format_instructions})

    try:
        # Parse JSON
        if isinstance(result, dict) and "text" in result:
            str = json.dumps(result["text"])
            parsed = json.loads(str)
        elif isinstance(result, str):
            parsed = json.loads(result)
        else:
            parsed = result
        
        entities = parsed.get("entities", {})
        if not entities or not isinstance(entities, dict):
            parsed["entities"] = {}
            return parsed     

        # Lấy từ khóa thời gian nếu AI trả
        time_keyword = entities.get("fromTime") or entities.get("toTime")

        # Tính ngày chính xác
        start_date, end_date = compute_revenue_dates(time_keyword, now)
        entities["fromTime"] = start_date.strftime("%Y-%m-%d")
        entities["toTime"] = end_date.strftime("%Y-%m-%d")

        parsed["entities"] = entities
        return parsed

    except Exception as e:
        print("⚠️ Lỗi xử lý kết quả:", e)
        print("Kết quả gốc:", result)
        return {"error": str(e), "raw": result}

def chatgpt_fallback(user_query: str) -> str:
    """
    Hàm fallback khi câu hỏi không nằm trong kịch bản doanh thu/chi phí/...,
    hoặc khi AI không nhận diện được intent hợp lệ.
    Tận dụng luôn llm đã khởi tạo ở đầu file.
    """
    try:
        # Dùng chính llm đã khai báo sẵn ở đầu file
        response = llm.invoke([
            {
                "role": "system",
                "content": "Bạn là trợ lý AI thân thiện, giúp người dùng trả lời câu hỏi một cách rõ ràng, ngắn gọn và tự nhiên bằng tiếng Việt."
            },
            {
                "role": "user",
                "content": user_query
            }
        ])
        # Nếu dùng ChatOpenAI, phản hồi là object -> lấy text
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        print("⚠️ Lỗi khi gọi fallback:", e)
        return "Xin lỗi, tôi chưa thể hiểu câu hỏi của bạn. Bạn có thể nói rõ hơn được không?"


# ====== Test nhanh ======
if __name__ == "__main__":
    test_queries = [
        "Thống kê doanh thu ngày hôm nay",
        "So sánh doanh thu tuần trước",
        "Doanh thu tháng này",
        "Tổng hợp doanh thu từ 01/11/2025 đến 05/11/2025"
    ]

    for q in test_queries:
        output = extract_intent_and_entities(q)
        print(json.dumps(output, indent=2, ensure_ascii=False))
