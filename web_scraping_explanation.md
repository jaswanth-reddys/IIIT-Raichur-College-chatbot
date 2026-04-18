# How Web Scraping Works

Web scraping is the automated process of extracting data from websites. Here is the step-by-step mechanism used in this project:

### 1. HTTP Request
The scraper sends an **HTTP GET request** to a specific URL (e.g., `https://iiitr.ac.in`) using libraries like `requests`. This is similar to a browser asking for a webpage.

### 2. Fetching HTML
The server responds with the **HTML source code** of the page. This contains the structure, text, and links of the website but without the visual styling.

### 3. Parsing
The raw HTML is parsed using a library like **BeautifulSoup**. It converts the text into a tree-like structure, making it easy to navigate and find specific elements (tags like `<a>`, `<p>`, `<div>`).

### 4. Data Extraction
The scraper looks for specific information:
- **Text Content**: Extracting the human-readable text from the page to build a knowledge base.
- **Links (URLs)**: Finding all `href` attributes in `<a>` tags to discover other pages on the same website.

### 5. Crawling (Recursion)
To gather information from the entire site, the scraper repeats the process for every new link it finds. To prevent infinite loops or crashing, it:
- Keeps track of **visited URLs**.
- Respects a **depth limit** (how many clicks away from the homepage it goes).

### 6. Storage/Usage
The extracted text is cleaned and stored. In this project, it is passed to the **LLM (Gemini)** as context, allowing the chatbot to answer questions based on the scraped content.

---

## Tools Used and Their Purpose

### Backend Tools
1. **Python**: The core programming language used for the backend logic.
2. **FastAPI**: A high-performance web framework for building APIs. It handles our `/ask` and `/refresh` endpoints.
3. **Uvicorn**: An ASGI server that runs our FastAPI application.
4. **Requests**: Used to send HTTP GET requests to fetch website HTML and Google Doc content.
5. **BeautifulSoup4 (bs4)**: A library for parsing HTML/XML. It allows us to extract text and links from the raw HTML we scrape.
6. **Google Generative AI (Gemini)**: The large language model (LLM) that powers the chatbot's conversational intelligence.
7. **Pydantic**: Used for data validation and defining the structure of API requests/responses.
8. **python-dotenv**: Manages environment variables like API keys securely.

### Frontend Tools (Assumed from structure)
1. **Next.js/React**: A powerful framework for building the user interface.
2. **PostCSS/Tailwind**: For styling the application efficiently.
3. **TypeScript**: Provides type safety for the frontend codebase.
