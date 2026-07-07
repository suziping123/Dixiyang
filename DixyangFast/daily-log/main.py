from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn
from app.chat.ai import LoadModel
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:63342"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def chat(question):
    model = LoadModel.load_model()
    response = model.invoke(question)
    return {"data":response.content}

@app.get("/chat/stream")
def chat_stream(question:str):
    def stream_chat(question:str):
        model = LoadModel.load_model()
        for chunk in model.stream(question):
            yield chunk.content
    return StreamingResponse(stream_chat(question),media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )