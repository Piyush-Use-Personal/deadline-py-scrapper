from fastapi import FastAPI, HTTPException, Response
from typing import Optional, List
from pydantic import BaseModel
from src.engine.engine import Engine

app = FastAPI()
engine = Engine()


class ProcessedContent(BaseModel):
    title: Optional[str] = None
    content: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    author: Optional[str] = None
    date: Optional[str] = None
    link: Optional[str] = None


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Screen Dollar application"}


@app.get("/run-engine", response_model=list[ProcessedContent])
async def run_engine():
    try:
        results = engine.run()  # Run the engine and get the aggregated results
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running engine: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
