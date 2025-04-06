from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
from io import BytesIO

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def process_pdf(pdf_file):
    pdf_reader = PdfReader(BytesIO(pdf_file.read()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    return vector_store

def get_answer(vector_store, question):
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in the 
    provided context just say, "answer is not available in the context", don't provide the wrong answer\n
    Context:\n {context}?\n
    Question: \n{question}\n 
    Answer:
    """
    
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    
    docs = vector_store.similarity_search(question)
    response = chain(
        {"input_documents": docs, "question": question},
        return_only_outputs=True
    )
    
    return response["output_text"]

def analyze_bid_requirements(text):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)

    prompt = f"""You are an expert bid analyzer. Please analyze this bid document text and provide a structured analysis:

{text}

Provide your analysis in the following format:

REQUIRED QUALIFICATIONS:
- List each qualification requirement
- If none found, state "No specific qualifications mentioned"

REQUIRED CERTIFICATIONS:
- List each certification requirement
- If none found, state "No specific certifications mentioned"

REQUIRED EXPERIENCE:
- List each experience requirement
- If none found, state "No specific experience requirements mentioned"

MISSING OR UNCLEAR REQUIREMENTS:
- List any vague or missing requirements
- If none found, state "No missing or unclear requirements identified"

ELIGIBILITY FLAGS:
- List any critical requirements that could disqualify a bid
- If none found, state "No eligibility issues identified"
"""

    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    response = model.invoke(prompt)
    return response.content

def analyze_checklist_requirements(text):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)

    prompt = f"""You are an expert RFP analyst. Please analyze this document and provide a structured checklist of submission requirements:

{text}

Provide your analysis in the following format:

DOCUMENT FORMAT REQUIREMENTS:
Provide a concise paragraph describing any formatting requirements found in the document, including page limits, font specifications, spacing, margins, or other formatting guidelines. If no specific format requirements are mentioned, state "No specific format requirements mentioned in the document."

REQUIRED ATTACHMENTS:
- List each required form/attachment
- Specify form numbers if provided
- Specify if original signatures required
- If none found, state "No specific attachments mentioned"

SUBMISSION FORMAT:
- Number of copies required
- Electronic/Physical submission
- File format for electronic submission
- If none specified, state "No specific format requirements mentioned"

ADDITIONAL REQUIREMENTS:
- Any other formatting or submission requirements
- If none found, state "No additional requirements identified"

Please be specific and precise in listing each requirement."""

    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    response = model.invoke(prompt)
    return response.content

def analyze_contract_risks(text):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)

    prompt = f"""You are an expert contract analyzer. Please analyze this contract document and identify potential risks and biased clauses:

{text}

Provide your analysis in the following format:

BIASED CLAUSES:
- List each identified biased clause
- Explain why it's disadvantageous
- If none found, state "No biased clauses identified"

TERMINATION RIGHTS:
- List any unilateral termination rights
- Analyze notice periods
- If none found, state "No concerning termination rights found"

LIABILITY AND INDEMNIFICATION:
- List any one-sided liability clauses
- Identify unfair indemnification requirements
- If balanced, state "Liability terms appear balanced"

SUGGESTED MODIFICATIONS:
- For each issue, provide specific modification suggestions
- Include recommended notice periods or balanced terms
- If no changes needed, state "No modifications suggested"

ADDITIONAL RISKS:
- List any other contract risks not covered above
- If none found, state "No additional risks identified"
"""

    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    response = model.invoke(prompt)
    return response.content

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        if 'pdf' not in request.files:
            return jsonify({"error": "No PDF file provided"}), 400
        
        pdf_file = request.files['pdf']
        question = request.form.get('question')
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        vector_store = process_pdf(pdf_file)
        answer = get_answer(vector_store, question)
        
        return jsonify({
            "question": question,
            "answer": answer
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/summary', methods=['POST'])
def generate_summary():
    try:
        if 'pdf' not in request.files:
            return jsonify({"error": "No PDF file provided"}), 400
        
        pdf_file = request.files['pdf']
        # Extract text from PDF
        pdf_reader = PdfReader(BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Generate analysis
        analysis = analyze_bid_requirements(text)
        
        return jsonify({
            "summary": analysis
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/checklist', methods=['POST'])
def generate_checklist():
    try:
        if 'pdf' not in request.files:
            return jsonify({"error": "No PDF file provided"}), 400
        
        pdf_file = request.files['pdf']
        # Extract text from PDF
        pdf_reader = PdfReader(BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Generate checklist
        checklist = analyze_checklist_requirements(text)
        
        return jsonify({
            "checklist": checklist
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/contract', methods=['POST'])
def analyze_contract():
    try:
        if 'pdf' not in request.files:
            return jsonify({"error": "No PDF file provided"}), 400
        
        pdf_file = request.files['pdf']
        # Extract text from PDF
        pdf_reader = PdfReader(BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Generate analysis
        analysis = analyze_contract_risks(text)
        
        return jsonify({
            "risks": analysis
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data or 'question' not in data:
            return jsonify({"error": "No question provided"}), 400
        
        question = data['question']
        
        # Initialize Gemini model for general chat
        model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
        
        # Get response from model
        response = model.invoke(question)
        
        return jsonify({
            "question": question,
            "answer": response.content
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
