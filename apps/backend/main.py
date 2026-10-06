from fastapi import FastAPI
from pydantic import BaseModel

from .orchestrator import CopilotOrchestrator

app = FastAPI(title="Alarm Investigation Copilot")
orchestrator = CopilotOrchestrator()


class ChatRequest(BaseModel):
    question: str


@app.get("/health")
async def health():
    return {"status": "ok", "service": "copilot-backend"}


@app.post("/chat")
async def chat(request: ChatRequest):
    if not request.question.strip():
        return {
            "answer": "Please enter an alarm investigation question.",
            "trace": [],
            "citations": [],
        }

    return await orchestrator.run(request.question)
