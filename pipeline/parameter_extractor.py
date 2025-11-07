import re
from datetime import datetime

def extract_parameters(user_query: str, api_config: dict) -> dict:
    """
    Trích xuất entity/param từ user_query (dạng cơ bản).
    """
    query = user_query.lower()
    params = {}

    # Chi nhánh
    branch_match = re.search(r"chi nhánh\s+([\w\s]+)", query)
    if branch_match:
        params["branch_name"] = branch_match.group(1).strip().title()

    # Quý / Tháng / Năm
    now = datetime.now()
    if "quý 1" in query or "q1" in query:
        params["revenue_start_date"] = f"{now.year}-01-01"
        params["revenue_end_date"] = f"{now.year}-03-31"
    elif "quý 2" in query or "q2" in query:
        params["revenue_start_date"] = f"{now.year}-04-01"
        params["revenue_end_date"] = f"{now.year}-06-30"
    elif "quý 3" in query or "q3" in query:
        params["revenue_start_date"] = f"{now.year}-07-01"
        params["revenue_end_date"] = f"{now.year}-09-30"
    elif "quý 4" in query or "q4" in query:
        params["revenue_start_date"] = f"{now.year}-10-01"
        params["revenue_end_date"] = f"{now.year}-12-31"
    elif "năm nay" in query:
        params["revenue_start_date"] = f"{now.year}-01-01"
        params["revenue_end_date"] = f"{now.year}-12-31"

    return params