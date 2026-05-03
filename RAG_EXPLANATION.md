# How RAG Works: Data Storage and Retrieval in IIITR Chatbot

This document explains the implementation of **Retrieval-Augmented Generation (RAG)** in this project, specifically how faculty-uploaded documents (PDF, Excel, JSON) are processed, stored, and retrieved using **ChromaDB**.

## 1. Overview of the RAG Process

RAG enhances the LLM (Gemini) by providing it with specific, private data that was not part of its original training set. The process follows these steps:
1. **Data Ingestion**: Faculty uploads a document.
2. **Processing**: The system extracts text based on the file type.
3. **Embedding**: Text is converted into numerical vectors (embeddings).
4. **Storage**: Vectors and original text are stored in **ChromaDB**.
5. **Retrieval**: When a user asks a question, the system finds the most relevant chunks from the database.
6. **Generation**: The retrieved context is sent to the LLM along with the user's question.

---

## 2. Data Ingestion & Processing

The system handles three main file formats through the `/upload-faculty-data` endpoint in `backend/main.py`:

### PDF Files
- **Tool**: `pypdf`
- **Process**: The system reads every page of the PDF and extracts all visible text.
- **Logic**: 
  ```python
  pdf = PdfReader(io.BytesIO(await file.read()))
  content = "\n".join([page.extract_text() for page in pdf.pages])
  ```

### Excel Files (XLSX/XLS)
- **Tool**: `pandas`
- **Process**: The system loads the spreadsheet and converts it into a string representation.
- **Logic**:
  ```python
  df = pd.read_excel(io.BytesIO(await file.read()))
  content = df.to_string()
  ```

### JSON Files
- **Tool**: Standard `json` library
- **Process**: The system parses the JSON and re-serializes it into a formatted string (pretty-print).
- **Logic**:
  ```python
  data = json.loads(await file.read())
  content = json.dumps(data, indent=2)
  ```

---

## 3. Storage in Vector Database (ChromaDB)

Once text is extracted, it is sent to the `add_to_vector_db` method in `backend/chatbot.py`.

### Chunking
To improve search accuracy, the system splits long documents into smaller "chunks" (paragraphs). 
- **Criteria**: Splits text by double newlines (`\n\n`) and filters out chunks shorter than 50 characters.

### Embeddings (Gemini Embedding Model)
Each chunk is converted into a vector using Google's **Gemini Embedding Model** (`models/gemini-embedding-001`). This turns text into a mathematical representation of its "meaning."

### Persistent Storage
- **Database**: **ChromaDB**
- **Location**: `./chroma_db` directory
- **Stored Data**:
  - **Embeddings**: The numerical vectors for search.
  - **Documents**: The original text content.
  - **Metadatas**: Information about the source file (filename and type).
  - **IDs**: Unique identifiers generated for each chunk.

---

## 4. The Retrieval Loop

When a user asks a question (e.g., "What is the faculty list?"):

1. **Query Embedding**: The user's question is converted into a vector using the same Gemini embedding model.
2. **Similarity Search**: ChromaDB calculates the "distance" between the question's vector and all stored document vectors.
3. **Top Results**: The system retrieves the top 3 most relevant chunks.
4. **Context Construction**: These chunks are appended to the LLM prompt under a "Relevant Context from Faculty" section.

```python
# From chatbot.py
prompt = f"""
...
Relevant Context from Faculty/Knowledge Base:
{vector_context}

Question: {question}
...
"""
```

This ensures that the AI answers based on the **actual data** provided by the faculty, rather than hallucinating information.
