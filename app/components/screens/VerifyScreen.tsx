"use client";
import { useState } from "react";

export default function VerifyScreen() {
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handlePdfFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setPdfFile(e.target.files[0]);
      setAnalysis(null);
    }
  };

  const handleDiscardPdf = () => {
    setPdfFile(null);
    setAnalysis(null);
  };

  const handleSubmit = async () => {
    if (!pdfFile) {
      alert("Please upload a PDF file");
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("pdf", pdfFile);

      const response = await fetch("http://localhost:5000/verify", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (response.ok) {
        setAnalysis(data);
      } else {
        throw new Error(data.error || "Failed to analyze RFP");
      }
    } catch (error) {
      alert(error instanceof Error ? error.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
      <h1 className="text-3xl font-bold text-black mb-2 font-serif">
        RFP Verification Tool
      </h1>
      <p className="text-gray-600 mb-6">
        Upload your RFP PDF to verify its eligibility.
      </p>

      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-all duration-200 relative mb-6 ${
          pdfFile
            ? "border-green-500 bg-green-50"
            : "border-gray-300 hover:border-blue-500"
        }`}
      >
        {pdfFile && (
          <button
            onClick={handleDiscardPdf}
            className="absolute top-2 right-2 p-1 rounded-full hover:bg-red-100 transition-colors"
            title="Remove file"
          >
            <svg
              className="w-5 h-5 text-red-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
        <div className="mb-4">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
            />
          </svg>
        </div>
        <label className="cursor-pointer block">
          <span className="text-gray-700 font-medium mb-2 block">
            Upload PDF File
          </span>
          <input
            type="file"
            onChange={handlePdfFileChange}
            className="hidden"
            accept=".pdf"
          />
          {pdfFile ? (
            <p className="text-sm text-green-600 mt-2 font-medium">
              ✓ {pdfFile.name}
            </p>
          ) : (
            <p className="text-sm text-gray-500 mt-2">Click to browse</p>
          )}
        </label>
      </div>

      <button
        onClick={handleSubmit}
        disabled={!pdfFile || loading}
        className={`w-full py-3 rounded-lg transition-all duration-200 font-medium mb-6
          ${
            loading
              ? "bg-gray-100 text-gray-400 cursor-wait"
              : !pdfFile
              ? "bg-gray-100 text-gray-400 cursor-not-allowed"
              : "bg-red-600 text-white hover:bg-red-700 active:bg-red-800 shadow-lg hover:shadow-red-200"
          }`}
      >
        {loading ? "Analyzing..." : "Verify RFP"}
      </button>

      {analysis && (
        <div className="mt-8">
          <h2 className="text-xl font-bold text-black mb-4">
            Analysis Results
          </h2>
          <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
            <div className="p-6 space-y-4">
              {analysis.split("\n").map((line: string, index: number) => {
                if (!line.trim()) return null;

                // Check if line is a heading (ends with ':')
                if (line.trim().endsWith(":")) {
                  return (
                    <h3
                      key={index}
                      className="text-black font-semibold text-lg mt-4"
                    >
                      {line.trim().replace(/\*\*/g, "")}
                    </h3>
                  );
                }

                // Handle bullet points
                if (line.trim().startsWith("-")) {
                  return (
                    <p key={index} className="text-black ml-4 flex items-start">
                      <span className="mr-2">•</span>
                      <span>
                        {line.trim().substring(1).trim().replace(/\*\*/g, "")}
                      </span>
                    </p>
                  );
                }

                // Regular text
                return (
                  <p key={index} className="text-black">
                    {line.trim().replace(/\*\*/g, "")}
                  </p>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
