# Project Progress: College Chatbot (IIITR)

## Completed Tasks:
- **Backend Initialization**: Created `backend/` directory.
- **Environment Setup**: Configured `.env` with Gemini API Key and `requirements.txt`.
- **Dependency Installation**: Installed `fastapi`, `uvicorn`, `google-generativeai`, `beautifulsoup4`, and `requests` in the virtual environment.
- **Web Scraper Implementation**: Created `backend/scraper.py` using BeautifulSoup to crawl `iiitr.ac.in`.
- **Chatbot Logic**: Created `backend/chatbot.py` to interface with Gemini-1.5-flash using scraped knowledge.
- **FastAPI Server**: Created `backend/main.py` for API endpoints.
- **Frontend Initialization**: Created `frontend/` using `npx create-next-app@latest` with TypeScript and Tailwind.
- **Chat Interface**: Developed a responsive chat UI in `frontend/src/app/page.tsx`.
- **CORS Configuration**: Enabled Cross-Origin Resource Sharing in FastAPI to allow frontend-backend communication.
- **Improved Startup**: Configured the backend to scrape `iiitr.ac.in` on startup and store knowledge.
