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


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


router = APIRouter()

@router.get("/query/")
async def query():

    assistant_response = {"answer": "Thanks for your input 🙏"}

        
    return assistant_response
