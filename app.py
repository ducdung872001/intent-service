from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
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

@app.post("/detect", response_class=PlainTextResponse)
async def get_detect(request: Request):    
    body = await request.json()
    query = body.get("query")
    
    # 🟩 lấy token từ header Authorization
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    response = run_pipeline(query, token=token)
    print('XZS')
    print(response)
    # return {"query": query, "result": response}
    return response