from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from .chains import full_chain

app = FastAPI()

# --- API 엔드포인트 ---
@app.get("/chat")
async def chat_rag(request: Request, user_message: str):
    async def event_generator():
        # 모든 질문은 full_chain을 통하도록 되돌립니다.
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
app.mount("/", StaticFiles(directory="static", html=True), name="static")

