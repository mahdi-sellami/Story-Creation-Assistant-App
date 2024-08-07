from dotenv import load_dotenv
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Request
from starlette.responses import StreamingResponse
from sqlalchemy.orm import Session
import shutil
import os
import logging
from pathlib import Path
import config
import json
from pydantic import BaseModel, Field
import datetime
from typing import Dict
from assistant.multi_agent_system_v2 import builder

from langgraph.checkpoint.memory import MemorySaver


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

thread = {"configurable": {"thread_id": "1"}}
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

router = APIRouter()

@router.get("/query/")
async def query():

    assistant_response = {"answer": "Thanks for your input 🙏"}

        
    return assistant_response

class StreamRequest(BaseModel):
    instruction: str
    details: str
    personas: Dict[str, str]  # Dictionary of string keys and string values

@router.post("/stream/")
async def stream(request: StreamRequest, graph=graph):
    graph = builder.compile(checkpointer=memory)
    response = graph.invoke({"instruction": request.instruction, "details": request.details, "personas":request.personas}, thread)
    chapter_graph = response.get("chapter_graph")
    for chapter_id, chapter in chapter_graph.items():
        return chapter


@router.post("/update/")
async def update(action_type: str, instructions: str):
    values = {}
    if action_type == "continue":
        values["continue_instructions"] = instructions
    elif action_type == "rewrite":
        values["rewrite_instructions"] = instructions
    response = graph.invoke(values, thread)
    chapter_graph = response.get("chapter_graph")
    for chapter_id, chapter in chapter_graph.items():
        return chapter