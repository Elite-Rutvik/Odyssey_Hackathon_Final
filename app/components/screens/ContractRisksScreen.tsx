import React, { useState } from "react";

const ReportView: React.FC<{ content: string }> = ({ content }) => {
  const formatContent = (text: string) => {
    // Clean the text by removing asterisks
    const cleanText = text.replace(/\*\*/g, "");

    // Split by sections while preserving section titles
    const sections = cleanText.split(
      /(?=BIASED CLAUSES|TERMINATION RIGHTS|LIABILITY AND INDEMNIFICATION|SUGGESTED MODIFICATIONS|ADDITIONAL RISKS)/g
    );

    return `
      <div class="space-y-6 text-black">
        ${sections
          .filter((section) => section.trim())
          .map((section) => {
            const [title, ...content] = section.split("\n");
            return `
              <div class="bg-white p-4 rounded-lg shadow-sm">
                <h3 class="font-bold text-lg text-black border-b border-gray-200 pb-2 mb-4">${title.trim()}</h3>
                <ul class="space-y-2">
                  ${content
                    .filter((line) => line.trim())
                    .map((line) => {
                      const cleanLine = line
                        .replace(/^[-*]\s*/, "")
                        .replace(/\*/g, "")
                        .trim();
                      return cleanLine
                        ? `<li class="text-black flex items-start">
                        <span class="mr-2 mt-1">•</span>
                        <span>${cleanLine}</span>
                      </li>`
                        : "";
                    })
                    .join("")}
                </ul>
              </div>
            `;
          })
          .join("")}
      </div>
    `;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg">
      <div className="px-8 py-6 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-black">
          Contract Risk Analysis Report
        </h2>
      </div>
      <div className="p-8">
        <div
          className="prose prose-lg max-w-none text-black"
          dangerouslySetInnerHTML={{
            __html: formatContent(content),
          }}
        />
      </div>
    </div>
  );
};

const ContractRisksScreen: React.FC = () => {
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [risks, setRisks] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const handlePdfFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setPdfFile(e.target.files[0]);
      setRisks("");
    }
  };

  const handleDiscardPdf = () => {
    setPdfFile(null);
    setRisks("");
  };

  const handleAnalyzeRisks = async () => {
    if (!pdfFile) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("pdf", pdfFile);

      const response = await fetch("http://localhost:5000/contract", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }

      setRisks(data.risks);
    } catch (error) {
      console.error("Error analyzing risks:", error);
      alert("Failed to analyze risks. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-extrabold mb-3 text-black">
          Contract Risk Analysis
        </h1>
        <p className="text-black text-lg mb-6">
          Analyze and assess potential risks in contract terms and conditions
        </p>

        <div
          className={`border-2 border-dashed rounded-lg p-6 text-center transition-all duration-200 relative mx-auto max-w-md ${
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

        {pdfFile && (
          <button
            onClick={handleAnalyzeRisks}
            disabled={loading}
            className="mt-4 bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors disabled:bg-blue-300"
          >
            {loading ? "Analyzing Risks..." : "Analyze Risks"}
          </button>
        )}
      </div>

      {risks && (
        <div className="mt-8">
          <div className="max-w-5xl mx-auto">
            <ReportView content={risks} />
          </div>
        </div>
      )}
    </div>
  );
};

export default ContractRisksScreen;
