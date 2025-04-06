import os
from dotenv import load_dotenv
from pypdf import PdfReader
import google.generativeai as genai

# Load environment variables
load_dotenv('.env.local')

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def analyze_bid_requirements(text):
    # Initialize Gemini
    api_key = os.getenv("GEMINI_API")
    if not api_key:
        raise ValueError("GEMINI_API key not found in environment variables")
    
    genai.configure(api_key=api_key)

    # Create prompt with structured output request
    prompt = f"""
    Analyze the following bid document and provide a structured analysis. 
    Format your response exactly as shown below:

    REQUIRED QUALIFICATIONS:
    - [List each qualification on a new line with bullet points]
    - [If none found, state "No specific qualifications mentioned"]

    REQUIRED CERTIFICATIONS:
    - [List each certification on a new line with bullet points]
    - [If none found, state "No specific certifications mentioned"]

    REQUIRED EXPERIENCE:
    - [List each experience requirement on a new line with bullet points]
    - [If none found, state "No specific experience requirements mentioned"]

    MISSING OR UNCLEAR REQUIREMENTS:
    - [List each missing/unclear requirement on a new line with bullet points]
    - [If none found, state "No missing or unclear requirements identified"]

    ELIGIBILITY FLAGS:
    - [List critical missing requirements that would make proposal ineligible]
    - [If none found, state "No eligibility issues identified"]

    Document text for analysis:
    {text}

    Remember to maintain the exact format with the headings and bullet points as shown above.
    """

    # Generate response using Gemini
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    # Format the response for better display
    formatted_response = response.text.strip()
    return formatted_response

def main():
    # Get PDF path from user
    pdf_path = input("Please enter the path to your PDF file: ")
    
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        
        # Analyze requirements
        analysis = analyze_bid_requirements(text)
        
        print("\nAnalysis Results:")
        print("-" * 50)
        print(analysis)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
