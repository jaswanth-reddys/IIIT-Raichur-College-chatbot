import os
import google.generativeai as genai
import requests
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()

# Load API keys from environment variables
def get_api_keys():
    keys = []
    # Primary key
    if os.environ.get("GOOGLE_API_KEY"):
        keys.append(os.environ.get("GOOGLE_API_KEY"))
    
    # Check for additional keys like GOOGLE_API_KEY_2, GOOGLE_API_KEY_3...
    i = 2
    while True:
        key = os.environ.get(f"GOOGLE_API_KEY_{i}")
        if not key:
            break
        keys.append(key)
        i += 1
    return keys

class IIITRChatbot:
    def __init__(self, knowledge_base_text="", doc_url=None):
        self.knowledge_base_text = knowledge_base_text
        self.doc_url = doc_url
        self.chat_history = []  # To store conversation history
        self.api_keys = get_api_keys()
        self.current_key_index = 0
        
        if not self.api_keys:
            raise ValueError("No Google API keys found in environment variables.")

        # Initialize Gemini model and configure API
        self._setup_api()

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(
            name="iiitr_knowledge")

    def _setup_api(self):
        """Configures the genai library with the current API key."""
        genai.configure(api_key=self.api_keys[self.current_key_index])
        self.model = genai.GenerativeModel("gemini-3-flash-preview")

    def _rotate_key(self):
        """Switches to the next available API key."""
        if len(self.api_keys) <= 1:
            return False
        
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        print(f"Quota exceeded or error. Switching to API key index {self.current_key_index}")
        self._setup_api()
        return True

    def _call_with_retry(self, func, *args, **kwargs):
        """Generic wrapper to call genai functions with key rotation logic."""
        max_retries = len(self.api_keys)
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_str = str(e).lower()
                # Check for quota exceeded (429) or related errors
                if "429" in error_str or "quota" in error_str or "limit" in error_str:
                    if self._rotate_key():
                        # If we rotate, we need to re-bind the function if it was a bound method
                        if hasattr(func, "__self__") and isinstance(func.__self__, genai.GenerativeModel):
                            # Re-use the updated self.model if it was a model method
                            new_func = getattr(self.model, func.__name__)
                            return self._call_with_retry(new_func, *args, **kwargs)
                        continue # Retry with new global config for module-level functions
                
                # If it's not a quota error or we've run out of keys
                if attempt == max_retries - 1:
                    raise e
                
                # For other errors, maybe try rotating anyway if it's transient?
                # But let's stick to quota for now.
                raise e

    def add_to_vector_db(self, text, metadata):
        """Adds text chunks to the vector database."""
        # Simple chunking by paragraph/newline for better retrieval
        chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 50]
        if not chunks:
            chunks = [text]

        for i, chunk in enumerate(chunks):
            # Generate embedding using Google AI
            embedding_result = self._call_with_retry(
                genai.embed_content,
                model="models/gemini-embedding-001",
                content=chunk,
                task_type="retrieval_document"
            )
            embedding = embedding_result['embedding']

            self.collection.add(
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[metadata],
                ids=[f"{metadata['source']}_{i}_{os.urandom(4).hex()}"]
            )

    def query_vector_db(self, query, n_results=3):
        """Queries the vector database for relevant context."""
        embedding_result = self._call_with_retry(
            genai.embed_content,
            model="models/gemini-embedding-001",
            content=query,
            task_type="retrieval_query"
        )
        query_embedding = embedding_result['embedding']

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return "\n".join(results['documents'][0]) if results['documents'] else ""

    def fetch_doc_content(self):
        if not self.doc_url:
            return ""

        try:
            # The doc URL provided is for a browser.
            # We need the export URL to get text easily.
            export_url = self.doc_url.replace(
                "/edit?usp=sharing", "/export?format=txt")
            response = requests.get(export_url, timeout=10)
            if response.status_code == 200:
                return response.text
            return ""
        except Exception as e:
            print(f"Error fetching Google Doc: {e}")
            return ""

    def answer_question(self, question):
        # 1. Get real-time content from Google Doc
        doc_content = self.fetch_doc_content()

        # 2. Get relevant content from Vector DB (Faculty uploads + Scraped data)
        vector_context = self.query_vector_db(question)

        # 3. Combine with static knowledge base
        full_kb = self.knowledge_base_text
        if doc_content:
            full_kb += "\n\nSource: Google Doc (Real-time update)\nContent: " + \
                doc_content
        if vector_context:
            full_kb += "\n\nRelevant Context from Faculty/Knowledge Base:\n" + vector_context

        # Format chat history for the prompt
        history_context = "\n".join(
            [f"{item['role']}: {item['content']}" for item in self.chat_history[-6:]])

        prompt = f"""You are an AI assistant for IIIT Raichur.
-------------------------
RESPONSE RULES
-------------------------
1. Always answer based ONLY on the knowledge base.
   If not found, say:
   "I'm not sure. Please check the official IIIT Raichur website."
2. Keep answers SHORT and DIRECT by default (1–3 sentences).
3. Only give a DETAILED answer IF:
   - The user explicitly asks for more details
   - The question requires explanation (e.g., "explain", "why", "how")
4. Do NOT assume a question is a follow-up unless the user clearly refers to previous context.
5. Do NOT repeat full information if already answered.
   - Provide only the missing or requested part.
6. For identity/contact questions:
   - Give ONLY the exact answer (name/role).
   - Do NOT include full biography unless asked.
7. Avoid unnecessary elaboration.
-------------------------
CONTEXT
-------------------------
Conversation History:
{history_context}

Knowledge Base:
{full_kb}
-------------------------
QUESTION:
{question}
"""

        try:
            response = self._call_with_retry(self.model.generate_content, prompt)
            answer = response.text

            # Update history
            self.chat_history.append({"role": "user", "content": question})
            self.chat_history.append({"role": "bot", "content": answer})

            return answer
        except Exception as e:
            return f"Error generating answer: {e}"


if __name__ == "__main__":
    # Test
    bot = IIITRChatbot(knowledge_base_text="IIITR is in Raichur, Karnataka.")
    print(bot.answer_question("Where is IIITR located?"))
