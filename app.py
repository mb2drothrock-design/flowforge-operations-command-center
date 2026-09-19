from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from flowforge import analyze_intake, insert_result, list_results

app = FastAPI(title="FlowForge API", version="1.0.0")


class IntakePayload(BaseModel):
    source: str = Field(default="api")
    subject: str
    text: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "flowforge"}


@app.get("/intake")
def get_intake(limit: int = 100) -> list[dict]:
    return list_results(limit=limit)


@app.post("/intake")
def create_intake(payload: IntakePayload) -> dict:
    result = analyze_intake(payload.source, payload.subject, payload.text).to_dict()
    result["id"] = insert_result(result)
    return result
