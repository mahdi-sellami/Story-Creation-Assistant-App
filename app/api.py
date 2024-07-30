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
import datetime
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

@router.get("/stream/")
async def stream(instruction: str, details: str):
    response = graph.invoke({"instruction": instruction, "details": details}, thread)
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