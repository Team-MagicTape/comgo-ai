from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

from .chains import full_chain
from .review_service.calculator import calculate_next_interval

app = FastAPI()

# --- Pydantic 모델 정의 ---
class ChatRequest(BaseModel):
    message: str

class ReviewIntervalRequest(BaseModel):
    is_correct: bool
    current_interval: int

class ReviewIntervalResponse(BaseModel):
    next_interval: int

# --- API 엔드포인트 ---

@app.post("/api/review/calculate-interval", response_model=ReviewIntervalResponse)
async def review_interval_api(request: ReviewIntervalRequest):
    """
    AI를 사용하여 망각 곡선에 기반한 최적의 다음 복습 주기를 계산합니다.
    """
    next_interval = await calculate_next_interval(
        is_correct=request.is_correct,
        current_interval=request.current_interval
    )
    return ReviewIntervalResponse(next_interval=next_interval)


@app.post("/api/chat")
async def chat_api_stream(request: ChatRequest):
    """
    (앱용) 채팅 요청을 받아 답변을 SSE (Server-Sent Events)로 스트리밍하는 API 엔드포인트입니다.
    """
    async def event_generator():
        # .astream()을 사용하여 체인을 스트리밍으로 실행합니다.
        stream = full_chain.astream({"input": request.message})
        
        async for chunk in stream:
            if await request.is_disconnected():
                break
            
            if isinstance(chunk, dict) and (answer := chunk.get("answer")):
                yield {"event": "message", "data": answer.replace("\n", "<br>")}
            elif isinstance(chunk, str):
                yield {"event": "message", "data": chunk.replace("\n", "<br>")}

        yield {"event": "end", "data": ""}

    return EventSourceResponse(event_generator())


@app.get("/chat")
async def chat_rag(request: Request, user_message: str):
    async def event_generator():
        stream = full_chain.astream({"input": user_message})
        
        async for chunk in stream:
            if await request.is_disconnected():
                break
            
            if isinstance(chunk, dict) and (answer := chunk.get("answer")):
                yield {"event": "message", "data": answer.replace("\n", "<br>")}
            elif isinstance(chunk, str):
                yield {"event": "message", "data": chunk.replace("\n", "<br>")}

        yield {"event": "end", "data": ""}

    return EventSourceResponse(event_generator())

# --- 정적 파일 마운트 ---
@app.get("/test-review", response_class=FileResponse)
async def read_test_page():
    return "static/test_review.html"

# 이 코드는 반드시 모든 API 엔드포인트 뒤에 위치해야 합니다.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
