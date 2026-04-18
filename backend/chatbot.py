import os
import google.generativeai as genai
import requests
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

class IIITRChatbot:
    def __init__(self, knowledge_base_text="", doc_url=None):
        self.knowledge_base_text = knowledge_base_text
        self.doc_url = doc_url
        self.model = genai.GenerativeModel("gemini-3-flash-preview")

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
        # Refresh Google Doc knowledge on every query for real-time updates
        doc_content = self.fetch_doc_content()
        full_kb = self.knowledge_base_text
        if doc_content:
            full_kb += "\n\nSource: Google Doc (Real-time update)\nContent: " + doc_content

        prompt = f"""
        You are an official chatbot for IIITR (Indian Institute of Information Technology, Raichur).
        Answer the following question based on the knowledge base provided below.
        If the information is not present, say you don't know but suggest visiting the official website.
        
        Question: {question}
        
        Knowledge Base:
        {full_kb}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating answer: {e}"

if __name__ == "__main__":
    # Test
    bot = IIITRChatbot(knowledge_base_text="IIITR is in Raichur, Karnataka.")
    print(bot.answer_question("Where is IIITR located?"))
