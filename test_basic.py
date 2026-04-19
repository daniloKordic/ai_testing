from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Item(BaseModel):
    name: str
    value: int

@app.get("/")
async def root():
    return {"message": "hello"}
