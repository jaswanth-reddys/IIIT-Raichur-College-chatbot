import os
import google.generativeai as genai
import requests
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

class IIITRChatbot:
    def __init__(self, knowledge_base_text="", doc_url=None):
        self.knowledge_base_text = knowledge_base_text
        self.doc_url = doc_url
        self.model = genai.GenerativeModel("gemini-3-flash-preview")
        self.chat_history = [] # To store conversation history
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(name="iiitr_knowledge")

    def add_to_vector_db(self, text, metadata):
        """Adds text chunks to the vector database."""
        # Simple chunking by paragraph/newline for better retrieval
        chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 50]
        if not chunks: chunks = [text]
        
        for i, chunk in enumerate(chunks):
            # Generate embedding using Google AI
            embedding_result = genai.embed_content(
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
        query_embedding = genai.embed_content(
            model="models/gemini-embedding-001",
            content=query,
            task_type="retrieval_query"
        )['embedding']
        
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
            export_url = self.doc_url.replace("/edit?usp=sharing", "/export?format=txt")
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
            full_kb += "\n\nSource: Google Doc (Real-time update)\nContent: " + doc_content
        if vector_context:
            full_kb += "\n\nRelevant Context from Faculty/Knowledge Base:\n" + vector_context

        # Format chat history for the prompt
        history_context = "\n".join([f"{item['role']}: {item['content']}" for item in self.chat_history[-6:]])

        prompt = f"""
        You are an official chatbot for IIITR (Indian Institute of Information Technology, Raichur).
        Answer the following question based on the knowledge base provided below.
        
        Rules for response length:
        1. If this is the FIRST time the user is asking about this specific topic or person in this conversation, provide a VERY SHORT and relevant answer (max 2 sentences).
        2. If the user is asking a follow-up question, or asking for more details about something already mentioned in the conversation history, provide a DETAILED and IN-DEPTH answer.
        
        If the information is not present in the knowledge base, say you don't know but suggest visiting the official website.
        
        Conversation History:
        {history_context}
        
        Question: {question}
        
        Knowledge Base:
        {full_kb}
        """
        
        try:
            response = self.model.generate_content(prompt)
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
