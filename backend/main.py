from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
    allow_origins=["*"], # In production, specify the actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for knowledge base and bot
# In a real-world scenario, you might want to cache or use a vector database
GOOGLE_DOC_URL = "https://docs.google.com/document/d/1ww3W8lzFRdnAHpzcXT7CVCouIuB9LtNIcKiBdiGv4_Y/edit?usp=sharing"
scraper = IIITRScraper()
# Initial scrape (can be expanded)
# scraper.scrape("https://iiitr.ac.in", depth=1) 
# To avoid slow startup during development, we can scrape on demand or use a sample
knowledge_text = "IIIT Raichur is a premier technical institute in Karnataka, India."
chatbot = IIITRChatbot(knowledge_base_text=knowledge_text, doc_url=GOOGLE_DOC_URL)

@app.on_event("startup")
def startup_event():
    global knowledge_text, chatbot
    print("Scraping iiitr.ac.in...")
    scraper.scrape("https://iiitr.ac.in", depth=2)
    knowledge_text = scraper.get_combined_text()
    chatbot.knowledge_base_text = knowledge_text
    print("Scraping complete.")

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

@app.post("/refresh")
async def refresh_knowledge_base():
    global knowledge_text, chatbot
    print("Re-scraping iiitr.ac.in...")
    scraper.knowledge_base = []
    scraper.visited_urls = set()
    scraper.scrape("https://iiitr.ac.in", depth=2)
    knowledge_text = scraper.get_combined_text()
    chatbot.knowledge_base_text = knowledge_text
    print("Refresh complete.")
    return {"message": "Knowledge base refreshed successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
