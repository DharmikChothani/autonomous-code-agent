from fastapi import FastAPI
from pydantic import BaseModel

from dotenv import load_dotenv
from .agent.graph import graph
from fastapi.middleware.cors import CORSMiddleware
import json
from backend.database.db import init_db
from backend.database.db import (
    create_run,
)
from backend.database.db import (
    get_runs,
    get_run,
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

load_dotenv()

app = FastAPI(
    title="Autonomous AI Coding Agent",
    version="1.0.0"
)
init_db()

origins = [
    "https://your-frontend-project.vercel.app",  # Production Vercel URL
    "http://localhost:3000",                     # Local Next.js / React
    "http://localhost:5173",                     # Local Vite
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_origin_regex=r"https://.*\.vercel\.app",  # Optional: allows all Vercel preview/branch URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Backend running on Render"}

class AgentRequest(BaseModel):
    task: str

@app.get("/")
def root():
    return {
        "message": "Autonomous AI Coding Agent API"
    }
@app.get("/api/runs")
def list_runs():

    return {
        "runs": get_runs()
    }

@app.post("/api/agent/stream")
def stream_agent(request: AgentRequest):

    def event_generator():

        initial_state = {
            "task": request.task,
            "plan": [],
            "current_step": 0,
            "generated_code": "",
            "test_code": "",
            "execution_result": "",
            "test_result": "",
            "review": "",
            "status": "started",
            "error": "",
            "retry_count": 0,
            "final_report": "",
        }

        accumulated_state = dict(initial_state)

        try:

            for event in graph.stream(
                initial_state,
                stream_mode="updates",
            ):

                for node_name, state_update in event.items():
                    if isinstance(state_update, dict):
                        accumulated_state.update(state_update)

                    payload = {
                        "type": "node",
                        "node": node_name,
                        "data": state_update,
                    }

                    yield (
                        f"data: "
                        f"{json.dumps(payload, default=str)}"
                        f"\n\n"
                    )

            if accumulated_state.get("status") in ("started", None):
                accumulated_state["status"] = "completed"

            create_run(request.task, accumulated_state)

            yield (
                "data: "
                + json.dumps({
                    "type": "done"
                })
                + "\n\n"
            )

        except Exception as e:
            accumulated_state["status"] = "failed"
            accumulated_state["error"] = str(e)
            create_run(request.task, accumulated_state)

            yield (
                "data: "
                + json.dumps({
                    "type": "error",
                    "error": str(e),
                })
                + "\n\n"
            )


    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

@app.post("/api/agent/run")
def run_agent(request: AgentRequest):
    
    initial_state = {

    "task": request.task,

    "plan": [],

    "current_step": 0,

    "generated_code": "",
    "test_code": "",

    "execution_result": "",
    "test_result": "",

    "review": "",

    "critic_result": "",
    "reflection": "",

    "quality_score": 0.0,

    "status": "started",
    "error": "",

    "retry_count": 0,

    "final_report": "",

    "events": [],
}

    result = graph.invoke(
    initial_state
)

    run_id = create_run(
    request.task,
    result,
)

    return {
    "run_id": run_id,
    **result,
}
   