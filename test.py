# app.py

import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import pandas as pd
from fpdf import FPDF
import os
from dotenv import load_dotenv
load_dotenv()       
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

st.set_page_config(page_title="RFP Analysis Dashboard", layout="wide")
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        font-family: 'Segoe UI', sans-serif;
    }
    .css-1d391kg, .css-1v0mbdj {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 AI-Powered RFP Analyzer")
st.caption("Analyze your RFP and company profile in one click")

# File uploads
col1, col2 = st.columns(2)
with col1:
    company_file = st.file_uploader("📁 Upload Company Profile (DOCX)", type=["docx"])
with col2:
    rfp_file = st.file_uploader("📁 Upload RFP Document (PDF)", type=["pdf"])

if company_file and rfp_file:
    with open("company.docx", "wb") as f:
        f.write(company_file.read())
    with open("rfp.pdf", "wb") as f:
        f.write(rfp_file.read())

    st.success("✅ Files uploaded. Analyzing...")

    # Load and split documents
    company_docs = Docx2txtLoader("company.docx").load()
    rfp_docs = PyPDFLoader("rfp.pdf").load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    company_chunks = splitter.split_documents(company_docs)
    rfp_chunks = splitter.split_documents(rfp_docs)

    # Embedding and vectorstore
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    company_vs = FAISS.from_documents(company_chunks, embeddings)
    rfp_vs = FAISS.from_documents(rfp_chunks, embeddings)

    company_relevant = company_vs.similarity_search("company certifications, registration, past performance", k=3)
    rfp_relevant = rfp_vs.similarity_search("eligibility criteria, mandatory qualifications", k=3)

    rfp_text = "\n".join([doc.page_content for doc in rfp_relevant])
    company_text = "\n".join([doc.page_content for doc in company_relevant])

    # LLM and Prompt Templates
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-8b", streaming=True)
    with open("evaluation_guidelines.txt", "r") as f:
        evaluation_guidelines=f.read()

    eligibility_prompt = PromptTemplate.from_template("""
    You are an expert in compliance and eligibility analysis for RFPs.
    Determine if the company is eligible to respond to the RFP based on the following criteria.
    mandatory qualifications such as:
    - Required experience 
    - Certifications
    - Licenses or registrations
                                                      
                                                      
    ## RFP:                                                  
    {rfp_chunk}

    ### Company Profile:
    {company_chunk}

    Respond in the format:
    ✅ Eligible: [Reason] even if  company structure, licenses, and personnel matches .
    or
    ❌ Not Eligible: [Reason]
    """)

    gap_prompt = PromptTemplate.from_template("""
    You are a proposal analyst identifying gaps between RFP requirements and a company's profile.

    Extract all mandatory qualifications such as:
    - Required experience
    - Certifications
    - Licenses or registrations
    - Other must-have conditions
    Use the following historical evaluation guidelines to support your decision:
    {guidelines}

    ### RFP:
    {rfp_chunk}

    ### Company Profile:
    {company_chunk}

    Return:
    ✅ Met Requirements:
    - [List with supporting RFP and profile text]

    ❌ Unmet Requirements:
    - [List with suggestions to fulfill or address each gap]
    """)

    submission_prompt = PromptTemplate.from_template("""
    You are a compliance assistant creating a submission checklist based on RFP instructions.

    From the text below, extract:
    - Document format (e.g., font, layout, margins)
    - Required attachments
    - Submission method and deadline

    ### RFP Submission Instructions:
    {rfp_chunk}

    Return as a checklist.
    """)

    risk_prompt = PromptTemplate.from_template("""
    You are a legal risk advisor. Review the RFP clauses and highlight potential risks or biased terms.
    
    For each, provide:
    - Clause (quoted or summarized)
    - Risk Level: Low, Medium, or High
    - Recommendation to mitigate the risk

    ### RFP Clauses:
    {rfp_chunk}
    """)

    eligibility_chain = LLMChain(llm=llm, prompt=eligibility_prompt, verbose=True)
    gap_chain = LLMChain(llm=llm, prompt=gap_prompt, verbose=True)
    submission_chain = LLMChain(llm=llm, prompt=submission_prompt, verbose=True)
    risk_chain = LLMChain(llm=llm, prompt=risk_prompt, verbose=True)
    with open("evaluation_guidelines.txt", "r") as f:
        evaluation_guidelines = f.read()

    # Run and display results
    st.header("🔍 RFP Analysis Results")

    with st.expander("✅ Eligibility & Compliance Checker"):
        st.info("Analyzing eligibility based on compliance requirements...")
        with st.spinner("🧠 Evaluating eligibility..."):
            eligibility_result = eligibility_chain.run({"rfp_chunk": rfp_text, "company_chunk": company_text, "guidelines": evaluation_guidelines})
        st.write(eligibility_result)

    with st.expander("📄 Criteria Extractor & Gap Analyzer"):
        st.info("Comparing company qualifications to mandatory RFP criteria...")
        with st.spinner("🧠 Evaluating eligibility..."):
            gap_result = gap_chain.run({"rfp_chunk": rfp_text, "company_chunk": company_text,"guidelines": evaluation_guidelines})
        st.write(gap_result)

    with st.expander("📋Submission Checklist Generator"):
        st.info("Creating checklist from submission instructions...")
        submission_result = submission_chain.run({"rfp_chunk": rfp_text})
        st.write(submission_result)

        # # Download button for submission checklist
        # if submission_result:
        #     csv_file = "checklist.csv"
        #     pdf_file = "checklist.pdf"

        #     # Save as CSV
        #     with open(csv_file, "w",encoding="utf-8") as f:
        #         f.write(submission_result)

        #     # Save as PDF
        #     pdf = FPDF()
        #     pdf.add_page()
        #     pdf.set_font("Arial", size=12)
        #     for line in submission_result.splitlines():
        #         pdf.multi_cell(0, 10, line)
        #     pdf.output(pdf_file)

        #     st.download_button("📥 Download Checklist (CSV)", data=open(csv_file, "rb",encoding="latin-1"), file_name=csv_file, mime="text/csv")
        #     st.download_button("📥 Download Checklist (PDF)", data=open(pdf_file, "rb",encoding="latin-1"), file_name=pdf_file, mime="application/pdf")

    with st.expander("⚠️ Risk Analyzer"):
        st.info("Detecting legal and contractual risks in the RFP...")
        risk_result = risk_chain.run({"rfp_chunk": rfp_text})
        st.write(risk_result)
