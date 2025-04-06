import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate 
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter 
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

st.title(" RFP Analysis Agent Suite")

VECTORSTORE_DIR = "faiss_index"

def build_and_save_vectorstore(documents, index_name):
    """
    Splits documents, generates embeddings, and saves vectorstore to disk.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embedding=embeddings)

    path = os.path.join(VECTORSTORE_DIR, index_name)
    os.makedirs(path, exist_ok=True)
    vectorstore.save_local(folder_path=path)

def load_vectorstore(index_name):
    """
    Loads a FAISS vectorstore from disk.
    """
    path = os.path.join(VECTORSTORE_DIR, index_name)
    embeddings = OpenAIEmbeddings() 
    return FAISS.load_local(folder_path=path, embeddings=embeddings,allow_dangerous_deserialization=True)

def query_vectorstore(vectorstore, query, k=3):
    return vectorstore.similarity_search(query, k=k)

def get_relevant_text(docs):
    return "\n".join([doc.page_content for doc in docs])



# File uploads
company_file = st.file_uploader("Upload Company Profile (DOCX)", type=["docx"])
rfp_file = st.file_uploader("Upload RFP Document (PDF)", type=["pdf"])

if company_file and rfp_file:
    with open("company.docx", "wb") as f:
        f.write(company_file.read())
    with open("rfp.pdf", "wb") as f:
        f.write(rfp_file.read())

    st.success("Files uploaded. Processing...")

    # Load and index documents
    company_docs = Docx2txtLoader("company.docx").load()
    rfp_docs = PyPDFLoader("rfp.pdf").load()

    # Build and save vectorstores (if not already exists)
    build_and_save_vectorstore(company_docs, "company")
    build_and_save_vectorstore(rfp_docs, "rfp")

    # Load vectorstores
    company_vs = load_vectorstore("company")
    rfp_vs = load_vectorstore("rfp")

    # Query relevant information
    company_relevant = query_vectorstore(company_vs, "company certifications, registration, past performance")
    rfp_relevant = query_vectorstore(rfp_vs, "eligibility criteria, mandatory qualifications")

    company_text = get_relevant_text(company_relevant)
    rfp_text = get_relevant_text(rfp_relevant)

    # Load LLM
    llm = ChatOpenAI(model_name="gpt-4o", streaming=True)

    # Define Prompts
    eligibility_prompt = PromptTemplate.from_template("""
    You are a compliance analyst assessing eligibility for RFP participation.
    
    Analyze the company profile against the eligibility criteria listed in the RFP. Consider certifications, legal registrations, years of experience, and any mandatory qualifications.

    ### RFP ELIGIBILITY CRITERIA:
    {rfp_chunk}

    ### COMPANY PROFILE:
    {company_chunk}

    Return only one of the following:
    -   **Eligible**: [Clearly explain why]
    -   **Not Eligible**: [Clearly explain what's missing or non-compliant]
    """)

    gap_prompt = PromptTemplate.from_template("""
    You are a gap analysis expert. Identify all mandatory qualifications, certifications, or criteria from the RFP and compare them with the company profile.

    ### RFP REQUIREMENTS:
    {rfp_chunk}

    ### COMPANY PROFILE:
    {company_chunk}

    Return in the following format:
    -  Met Requirements:
      - [Requirement 1]
      - [Requirement 2]
    -   Unmet Requirements:
      - [Requirement]: [Why it is missing or insufficient]
      - Suggestion: [How to address or mitigate the gap]
    """)

    submission_prompt = PromptTemplate.from_template("""
    You are a proposal checklist generator.

    From the RFP text below, extract all submission instructions. Create a checklist that includes:
    - 📄 Document formatting (font size, spacing, margins, file types)
    - 📌 Required attachments or forms
    - 📅 Submission deadlines
    - 📤 Submission method (email, portal, physical)

    ### RFP SUBMISSION DETAILS:
    {rfp_chunk}

    Return as a bullet-point checklist grouped by category.
    """)

    risk_prompt = PromptTemplate.from_template("""
    You are a legal risk analyzer. Review the following RFP text for clauses that may introduce legal, financial, or operational risk to a vendor.

    For each risky or biased clause, provide:
    - 🔍 Clause (quote it)
    - ⚠️ Risk Level (Low / Medium / High)
    - 💡 Suggestion (how to rephrase, negotiate, or respond)

    ### RFP CLAUSES:
    {rfp_chunk}

    Only return findings that clearly carry potential risk.
    """)

    # Chains
    eligibility_chain = LLMChain(llm=llm, prompt=eligibility_prompt, verbose=True)
    gap_chain = LLMChain(llm=llm, prompt=gap_prompt, verbose=True)
    submission_chain = LLMChain(llm=llm, prompt=submission_prompt, verbose=True)
    risk_chain = LLMChain(llm=llm, prompt=risk_prompt, verbose=True)

    # Run agents and display results
    st.subheader("Eligibility & Compliance Checker")
    st.write(eligibility_chain.run({"rfp_chunk": rfp_text, "company_chunk": company_text}))

    st.subheader("Criteria Extractor & Gap Analyzer")
    st.write(gap_chain.run({"rfp_chunk": rfp_text, "company_chunk": company_text}))

    st.subheader("Submission Checklist Generator")
    st.write(submission_chain.run({"rfp_chunk": rfp_text}))

    st.subheader("Risk Analyzer")
    st.write(risk_chain.run({"rfp_chunk": rfp_text}))
