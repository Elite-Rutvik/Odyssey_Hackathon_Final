"use client";

declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition;
    webkitSpeechRecognition: typeof SpeechRecognition;
  }
}

import { useState, useRef, useEffect } from "react";
import {
  MicrophoneIcon,
  PaperClipIcon,
  PaperAirplaneIcon,
  StopIcon,
} from "@heroicons/react/24/outline";

interface Message {
  text: string;
  isUser: boolean;
  timestamp: Date;
  file?: {
    name: string;
    type: string;
    isNew?: boolean; // Add this to identify when file is first attached
  };
}

interface ApiResponse {
  question: string;
  answer: string;
}

export default function ChatScreen() {
  // Add new ref for messages container
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<Message[]>([
    {
      text: "Hello! How can I assist you today?",
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // Add scroll to bottom effect
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;

        recognitionRef.current.onresult = (event) => {
          const transcript = Array.from(event.results)
            .map((result) => result[0].transcript)
            .join("");
          setInputText(transcript);
        };

        recognitionRef.current.onerror = (event) => {
          console.error("Speech recognition error:", event.error);
          setIsRecording(false);
        };
      }
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.start();
      setIsRecording(true);
    } else {
      alert("Speech recognition is not supported in your browser");
    }
  };

  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const sendPdfQuestion = async (file: File, question: string) => {
    const formData = new FormData();
    formData.append("pdf", file);
    formData.append("question", question);

    try {
      const response = await fetch("http://localhost:5000/ask", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to get answer");
      }

      const data: ApiResponse = await response.json();
      return data.answer;
    } catch (error) {
      console.error("Error:", error);
      return "Sorry, I encountered an error processing your request.";
    }
  };

  const sendNormalQuestion = async (question: string) => {
    try {
      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        throw new Error("Failed to get answer");
      }

      const data: ApiResponse = await response.json();
      return data.answer;
    } catch (error) {
      console.error("Error:", error);
      return "Sorry, I encountered an error processing your request.";
    }
  };

  const handleSend = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      text: inputText,
      isUser: true,
      timestamp: new Date(),
      file: selectedFile && {
        name: selectedFile.name,
        type: selectedFile.type,
        isNew: true,
      },
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText("");

    const processingMessage: Message = {
      text: "Processing your request...",
      isUser: false,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, processingMessage]);

    let answer;
    if (selectedFile) {
      answer = await sendPdfQuestion(selectedFile, inputText);
    } else {
      answer = await sendNormalQuestion(inputText);
    }

    setMessages((prev) => prev.filter((msg) => msg !== processingMessage));

    const aiResponse: Message = {
      text: answer,
      isUser: false,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, aiResponse]);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="bg-gradient-to-br from-red-50 via-white to-red-50 rounded-xl border border-gray-200 shadow-lg h-[calc(100vh-12rem)] flex flex-col overflow-hidden">
      {/* Chat Header */}
      <div className="p-6 border-b border-gray-200 bg-white/80 backdrop-blur-sm">
        <h2 className="text-2xl font-bold text-gray-800 font-serif">
          AI Assistant
        </h2>
        <p className="text-gray-500 font-light">
          Ready to help you analyze RFPs
        </p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gradient-to-b from-transparent to-red-50/30">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.isUser ? "justify-end" : "justify-start"
            } animate-fade-in`}
          >
            <div
              className={`max-w-[80%] p-4 rounded-2xl shadow-sm transition-all duration-200 ${
                message.isUser
                  ? "bg-gradient-to-r from-red-600 to-red-500 text-white rounded-tr-none transform hover:-translate-y-1"
                  : "bg-white text-gray-800 rounded-tl-none transform hover:-translate-y-1"
              }`}
            >
              <p className="text-sm font-medium leading-relaxed">
                {message.text}
              </p>
              {message.file?.isNew && (
                <div className="mt-2 text-xs flex items-center gap-2 bg-black/10 rounded-lg p-2">
                  <PaperClipIcon className="w-4 h-4" />
                  <span className="opacity-90 font-medium">
                    {message.file.name}
                  </span>
                </div>
              )}
              <span className="text-xs mt-2 block opacity-70 font-light">
                {message.timestamp.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} /> {/* Add this div for auto-scroll */}
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200 bg-white/80 backdrop-blur-sm">
        {selectedFile && (
          <div className="mb-3 flex items-center gap-2 bg-blue-50 p-2 rounded-lg w-fit animate-fade-in">
            <span className="text-xs text-blue-700 font-medium truncate max-w-[200px]">
              {selectedFile.name}
            </span>
            <button
              onClick={() => setSelectedFile(null)}
              className="p-1 hover:bg-blue-100 rounded-full transition-all duration-200"
            >
              <svg
                className="w-3 h-3 text-blue-700"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        )}
        <div className="flex items-center gap-3 bg-gray-50 p-2 rounded-xl shadow-sm">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            accept=".pdf"
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-2.5 hover:bg-white rounded-lg transition-all duration-200 hover:shadow-md"
          >
            <PaperClipIcon className="w-5 h-5 text-gray-600" />
          </button>
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`p-2.5 rounded-lg transition-all duration-200 hover:shadow-md ${
              isRecording
                ? "bg-red-100 text-red-600 animate-pulse"
                : "hover:bg-white text-gray-600"
            }`}
          >
            {isRecording ? (
              <StopIcon className="w-5 h-5" />
            ) : (
              <MicrophoneIcon className="w-5 h-5" />
            )}
          </button>
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
            placeholder="Type your message here..."
            className="flex-1 p-3 rounded-lg border-0 bg-transparent focus:ring-0 text-gray-800 placeholder-gray-400 font-medium"
          />
          <button
            onClick={handleSend}
            disabled={!inputText.trim() && !selectedFile}
            className={`p-2.5 rounded-lg transition-all duration-200 ${
              inputText.trim() || selectedFile
                ? "bg-gradient-to-r from-red-600 to-red-500 text-white hover:shadow-lg hover:shadow-red-200"
                : "bg-gray-200 text-gray-400"
            }`}
          >
            <PaperAirplaneIcon className="w-5 h-5 transform rotate-90" />
          </button>
        </div>
      </div>
    </div>
  );
}

// Add these styles to your global CSS file or add them here
const styles = `
@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out forwards;
}
`;
