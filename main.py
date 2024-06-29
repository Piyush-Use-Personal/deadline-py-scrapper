from fastapi import FastAPI, HTTPException
from web_processor import WebProcessor
from pydantic import BaseModel

app = FastAPI()
web_processor = WebProcessor()

class URLRequest(BaseModel):
    url: str

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application"}

@app.post("/process/")
async def process_website(request: URLRequest):
    try:
        url = request.url
        results = web_processor.process(url)
        return {"message": "Processing completed", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing URL: {str(e)}")
