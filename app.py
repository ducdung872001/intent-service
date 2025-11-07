from fastapi import FastAPI
from pipeline.intent_detector import extract_intent_and_entities
from pipeline.main_pipeline import run_pipeline

app = FastAPI(title="AI Intent Service")

@app.post("/intent")
async def get_intent(payload: dict):
    query = payload.get("query")
    result = extract_intent_and_entities(query)
    return {"query": query, "result": result}

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.post("/detect")
async def get_detect(payload: dict):    
    query = payload.get("query")
    response = run_pipeline(query)
    return {"query": query, "result": response}

if __name__ == "__main__":
    query = "Thống kê doanh thu quý 3 năm nay của chi nhánh Thái Hà"
    response = run_pipeline(query)
    print("\n[Bot]:", response)