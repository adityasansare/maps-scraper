from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import pandas as pd
import io
import threading
from scraper import scrape_google_maps
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse


app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://maps-scraper-taupe.vercel.app"],  # or your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

scraped_data = []
lock = threading.Lock()

# Pydantic model for request body
class QueryRequest(BaseModel):
    query: str

@app.post("/scrape")
async def scrape_endpoint(request: QueryRequest = Body(...)):
    global scraped_data
    try:
        data = scrape_google_maps(request.query)
        with lock:
            scraped_data = data
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download_csv")
def download_csv():
    with lock:
        if not scraped_data:
            raise HTTPException(status_code=404, detail="No scraped data found")
        df = pd.DataFrame(scraped_data)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    stream.seek(0)
    headers = {"Content-Disposition": "attachment; filename=mumbai_places.csv"}
    return StreamingResponse(iter([stream.getvalue()]), media_type="text/csv", headers=headers)
