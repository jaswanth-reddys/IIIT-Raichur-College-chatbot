"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function Home() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    const baseUrl = (process.env.NEXT_PUBLIC_API_URL || 'https://iiit-raichur-college-chatbot.onrender.com').replace(/\/$/, '');
    
    try {
      const response = await fetch(`${baseUrl}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      const data = await response.json();
      const botMessage = { role: "bot", content: data.answer };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error: any) {
      console.error("Error:", error);
      setMessages((prev) => [...prev, { 
        role: "bot", 
        content: `⚠️ Connection Error: ${error.message || "Make sure the backend is running."}` 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    const baseUrl = (process.env.NEXT_PUBLIC_API_URL || 'https://iiit-raichur-college-chatbot.onrender.com').replace(/\/$/, '');

    try {
      const response = await fetch(`${baseUrl}/upload-faculty-data`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (response.ok) {
        setMessages((prev) => [...prev, { role: "bot", content: `✅ ${data.message}` }]);
      } else {
        setMessages((prev) => [...prev, { role: "bot", content: `❌ Upload failed: ${data.detail || response.statusText}` }]);
      }
    } catch (error: any) {
      console.error("Upload error:", error);
      setMessages((prev) => [...prev, { role: "bot", content: `❌ Error connecting to server: ${error.message}` }]);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="min-h-screen bg-transparent relative">
      {/* Floating Chat Bubble */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed bottom-6 right-6 w-16 h-16 bg-blue-600 rounded-full shadow-2xl flex items-center justify-center text-white hover:bg-blue-700 transition-all duration-300 z-50 transform hover:scale-110 active:scale-95 ${
          isOpen ? "scale-0 opacity-0 pointer-events-none" : "scale-100 opacity-100"
        }`}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      </button>

      {/* Chat Window */}
      <div
        className={`fixed bottom-6 right-6 w-[85vw] md:w-[320px] h-[400px] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden transition-all duration-300 origin-bottom-right z-50 border border-blue-100 ${
          isOpen ? "scale-100 opacity-100" : "scale-0 opacity-0 pointer-events-none"
        }`}
      >
        {/* Header */}
        <header className="bg-white p-4 flex items-center justify-between border-b border-blue-50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full overflow-hidden flex items-center justify-center border border-blue-50">
              <img src="/logo.png" alt="Logo" className="w-full h-full object-contain" />
            </div>
            <div>
              <h2 className="text-zinc-800 font-semibold">IIITR Bot</h2>
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                <span className="text-zinc-500 text-xs">Online</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-1">
            {/* Faculty Upload Button */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              className="hidden"
              accept=".pdf,.json,.xlsx,.xls"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              title="Faculty: Upload Data (PDF, JSON, XLSX)"
              className="p-2 text-zinc-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
            >
              {isUploading ? (
                <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
              )}
            </button>

            {/* Close Button */}
            <button
              onClick={() => setIsOpen(false)}
              className="p-2 text-zinc-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
              title="Close Chat"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </header>

        {/* Chat Content */}
        <main className="flex-1 overflow-y-auto p-4 space-y-4 bg-white scrollbar-thin scrollbar-thumb-blue-100 scrollbar-track-transparent">
          {messages.length === 0 && (
            <div className="text-center py-10">
              <p className="text-zinc-400 text-xs font-medium">Hello! How can I help you today?</p>
            </div>
          )}
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] p-3 rounded-2xl text-xs ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white rounded-tr-none shadow-md"
                    : "bg-blue-50 text-zinc-800 rounded-tl-none border border-blue-100"
                }`}
              >
                {msg.role === "bot" ? (
                  <div className="prose prose-xs max-w-none prose-zinc">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                  </div>
                ) : (
                  msg.content
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-blue-50 p-3 rounded-2xl rounded-tl-none border border-blue-100 text-blue-400 text-xs flex gap-1">
                <span className="animate-bounce">.</span>
                <span className="animate-bounce delay-100">.</span>
                <span className="animate-bounce delay-200">.</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </main>

        {/* Footer Input */}
        <footer className="p-4 bg-white border-t border-blue-50">
          <div className="relative flex items-center">
            <input
              type="text"
              className="flex-1 p-3 pr-12 bg-white border border-blue-100 rounded-2xl text-zinc-800 text-xs focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-zinc-400 shadow-sm"
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
            />
            <button
              onClick={handleSend}
              disabled={isLoading}
              className="absolute right-1.5 p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:bg-blue-400 transition-colors shadow-lg"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 rotate-90" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
              </svg>
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
}
