from fastapi import FastAPI, HTTPException
from web_processor import WebProcessor
from pydantic import BaseModel

app = FastAPI()
web_processor = WebProcessor()

class URLRequest(BaseModel):
    url: str

class ProcessedContent(BaseModel):
    title: str
    content: list
    author: str

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application"}

@app.post("/process/", response_model=list[ProcessedContent])
async def process_website(request: URLRequest):
    try:
        url = request.url
        results = web_processor.process(url)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing URL: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)