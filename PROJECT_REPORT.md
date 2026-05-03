# Project Report: IIITR Intelligent Campus Chatbot

## 1. Introduction
The **IIITR Intelligent Campus Chatbot** is a comprehensive AI-driven solution designed to serve as an official information portal for the Indian Institute of Information Technology, Raichur (IIITR). Developed using state-of-the-art Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) techniques, the chatbot provides students, faculty, and visitors with instant, accurate, and context-aware responses to queries regarding campus life, admissions, faculty details, and institutional policies.

## 2. Motivation
In a rapidly evolving educational environment, the volume of information available on institutional websites can be overwhelming. Traditional search methods often fail to provide direct answers to complex queries, leading to information fragmentation. The motivation behind this project is to:
- **Centralize Information**: Provide a single point of contact for all institutional data.
- **Improve Accessibility**: Offer 24/7 assistance without human intervention.
- **Enhance User Experience**: Deliver a conversational interface that understands natural language and provides relevant, concise information.
- **Support Faculty**: Enable faculty members to dynamically update the knowledge base with specialized documents.

## 3. Objectives
The primary objectives of the project are:
1. To develop a robust web scraper capable of indexing the IIITR official website.
2. To implement a dynamic knowledge base that integrates real-time data from Google Docs.
3. To build a Retrieval-Augmented Generation (RAG) pipeline using a vector database for efficient document retrieval.
4. To create a modern, responsive frontend with a floating chat interface.
5. To implement adaptive response logic that provides concise summaries for new topics and in-depth details for follow-up queries.

## 4. Methodology
The project follows a modular architecture consisting of a **FastAPI** backend and a **Next.js** frontend.

### 4.1 Backend Architecture
The backend is the core engine of the chatbot, responsible for data ingestion, processing, and response generation.

#### 4.1.1 Web Scraping
The project employs a custom-built web scraper ([./backend/scraper.py](./backend/scraper.py)) using `BeautifulSoup` and `requests`. 
- **Traversal**: It recursively crawls the IIITR website up to a specified depth (default depth 2).
- **Extraction**: It extracts clean text content while filtering out irrelevant HTML boilerplate.
- **Aggregation**: The scraped data is aggregated into a consolidated knowledge base that the LLM uses for context.

#### 4.1.2 Google Docs Integration
To allow for real-time updates without redeploying code, the chatbot integrates with a live Google Doc.
- **Live Syncing**: The `fetch_doc_content` method in [./backend/chatbot.py](./backend/chatbot.py) converts a shared Google Doc URL into an exportable text format.
- **Immediate Availability**: Every query triggers a check for the latest document content, ensuring the bot always has the most current information provided by administrators.

#### 4.1.3 Retrieval-Augmented Generation (RAG)
The RAG pipeline is implemented to handle large volumes of unstructured data (PDFs, XLSX, JSON) uploaded by faculty members.
- **Vector Database**: **ChromaDB** is used as a persistent vector store.
- **Embeddings**: Content is converted into high-dimensional vectors using the `models/gemini-embedding-001` model.
- **Semantic Search**: When a user asks a question, the system performs a similarity search in the vector DB to retrieve the most relevant context chunks.
- **Context Injection**: These chunks are injected into the Gemini model's prompt, enabling it to answer questions based on specific uploaded documents.

### 4.2 Frontend Design
The frontend is built with **Next.js** and **Tailwind CSS**, featuring:
- **Floating Chat Bubble**: A fixed-position UI component for easy access.
- **Dark Mode Support**: A professional zinc-dark theme optimized for readability.
- **Faculty Portal**: An integrated upload feature that allows authorized users to contribute documents (PDF, Excel, JSON) directly through the interface.

## 5. Technical Stack
- **Frontend**: Next.js, React, Tailwind CSS, Lucide Icons.
- **Backend**: FastAPI, Python, Uvicorn.
- **AI Models**: openai/gpt-oss-120b (Generation), Gemini Embedding 001.
- **Database**: ChromaDB (Vector Store).
- **Tools**: BeautifulSoup (Scraping), PyPDF (PDF Parsing), Pandas (Excel Processing).

## 6. Conclusion
The IIITR Intelligent Campus Chatbot represents a significant step toward a more connected and informed campus. By leveraging RAG and automated scraping, the system ensures that information is always accurate and easily accessible. The modular nature of the backend allows for future expansions, such as voice integration or multi-language support.


1. Where it is stored
The data is stored in three different ways:

Website Content: When the server starts, it scrapes the IIITR website and stores all the text in an in-memory variable called knowledge_text in main.py.
Faculty Uploads (PDF/Excel/JSON): These are processed and stored in a Vector Database (ChromaDB) located in the ./chroma_db directory. This allows for semantic search based on the user's question.
Real-time Admin Data: Stored in a Google Doc. The bot fetches the latest text from this document for every single query to ensure it has the most up-to-date information.