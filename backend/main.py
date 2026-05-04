from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from pypdf import PdfReader
import json
import io
try:
    from .scraper import IIITRScraper
    from .chatbot import IIITRChatbot
except ImportError:
    from scraper import IIITRScraper
    from chatbot import IIITRChatbot
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "keys_configured": len(chatbot.api_keys),
        "vector_db": "initialized"
    }

# Global variables for knowledge base and bot
GOOGLE_DOC_URL = "https://docs.google.com/document/d/1ww3W8lzFRdnAHpzcXT7CVCouIuB9LtNIcKiBdiGv4_Y/edit?usp=sharing"
scraper = IIITRScraper()
# Initial sample knowledge to ensure the bot works immediately
knowledge_text = "IIIT Raichur is a premier technical institute in Karnataka, India."
chatbot = IIITRChatbot(knowledge_base_text=knowledge_text, doc_url=GOOGLE_DOC_URL)

import threading

def run_initial_scrape():
    global knowledge_text, chatbot
    print("Performing initial scrape in background...")
    try:
        scraper.scrape("https://iiitr.ac.in", depth=2)
        knowledge_text = scraper.get_combined_text()
        chatbot.knowledge_base_text = knowledge_text
        print("Initial scrape complete.")
    except Exception as e:
        print(f"Startup scrape failed: {e}")

@app.on_event("startup")
def startup_event():
    # Run scraping in a separate thread to avoid blocking startup (important for Render/Cloud)
    thread = threading.Thread(target=run_initial_scrape)
    thread.start()

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "IIITR Chatbot API is running"}

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    if not request.question:
        raise HTTPException(status_code=400, detail="Question is empty")
    
    answer = chatbot.answer_question(request.question)
    return {"answer": answer}

@app.post("/upload-faculty-data")
async def upload_faculty_data(file: UploadFile = File(...)):
    global chatbot
    content = ""
    filename = file.filename
    
    try:
        if filename.endswith(".pdf"):
            pdf = PdfReader(io.BytesIO(await file.read()))
            content = "\n".join([page.extract_text() for page in pdf.pages])
        
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            df = pd.read_excel(io.BytesIO(await file.read()))
            content = df.to_string()
            
        elif filename.endswith(".json"):
            data = json.loads(await file.read())
            content = json.dumps(data, indent=2)
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, JSON, or XLSX.")

        if not content.strip():
            raise HTTPException(status_code=400, detail="File is empty or could not be parsed.")

        # Add to vector database
        chatbot.add_to_vector_db(content, {"source": filename, "type": "faculty_upload"})
        
        return {"message": f"Successfully processed {filename} and updated knowledge base."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/refresh")
async def refresh_knowledge_base():
    global knowledge_text, chatbot
    print("Re-scraping iiitr.ac.in (triggered via API)...")
    try:
        scraper.knowledge_base = []
        scraper.visited_urls = set()
        scraper.scrape("https://iiitr.ac.in", depth=2)
        knowledge_text = scraper.get_combined_text()
        chatbot.knowledge_base_text = knowledge_text
        print("Refresh complete.")
        return {"message": "Knowledge base refreshed successfully in-memory"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
