import streamlit as st
import PyPDF2
from typing import List, Tuple
import os
import google.generativeai as genai  # Changed import statement
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.graphs import Neo4jGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Neo4jVector
from langchain.embeddings import VertexAIEmbeddings
from langchain.llms import VertexAI
from langchain_core.language_models.llms import LLM
from typing import Any, List, Optional
from langchain_core.pydantic_v1 import BaseModel, Field, PrivateAttr

# Neo4j credentials - Updated URI format
NEO4J_URI = "neo4j+s://3f57e783.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "WFjhW_fw7H5d-zKym-dKIaupKTzHaHnycLCzOorHYFk"

# Initialize Google Gemini model with new client
genai.configure(api_key="")
model = genai.GenerativeModel('gemini-pro')  # Changed client to model

def extract_text_from_pdf(pdf_file) -> str:
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def create_graph():
    try:
        graph = Neo4jGraph(
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD
        )
        # Test connection with a simple query
        try:
            graph.query("MATCH (n) RETURN n LIMIT 1")
            st.success("Successfully connected to Neo4j database!")
            return graph
        except Exception as query_error:
            st.error(f"Connected to database but query failed: {str(query_error)}")
            return None
    except Exception as e:
        st.error(f"Failed to connect to Neo4j: {str(e)}")
        st.info("Please check:\n1. Database is running\n2. Credentials are correct\n3. Database allows remote connections")
        return None

class GeminiWrapper(LLM):
    def __init__(self, model):
        super().__init__()
        self.model = model
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.error(f"Error generating content: {str(e)}")
            return ""

    @property
    def _identifying_params(self) -> dict:
        return {"model": "gemini-pro"}
    
    @property
    def _llm_type(self) -> str:
        return "gemini"

    def predict(self, text: str) -> str:
        return self._call(text)

    def with_structured_output(self, output_schema: Any):
        return self

def process_text_for_kg(text: str):
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    documents = text_splitter.create_documents([text])
    
    # Create graph transformer and custom wrapper for Gemini
    graph = create_graph()
    if graph is None:
        return None
    
    try:
        llm = GeminiWrapper(model)
        llm_transformer = LLMGraphTransformer(llm=llm)
        
        # Convert to graph documents with more explicit error handling
        try:
            graph_documents = llm_transformer.convert_to_graph_documents(documents)
        except Exception as e:
            st.error(f"Failed to convert documents to graph format: {str(e)}")
            return None
        
        # Add to Neo4j
        graph.add_graph_documents(
            graph_documents,
            baseEntityLabel=True,
            include_source=True
        )
        return graph
    except Exception as e:
        st.error(f"Failed to create knowledge graph: {str(e)}")
        st.info("Error details: " + str(e))
        return None

def setup_vector_store():
    embeddings = VertexAIEmbeddings()
    
    return Neo4jVector.from_existing_graph(
        embeddings,
        search_type="hybrid",
        node_label="Document",
        text_node_properties=["text"],
        embedding_node_property="embedding"
    )

def answer_question(question: str, vector_store, graph):
    try:
        # Create QA prompt
        prompt_template = """Based on the following context, please answer the question.
        Context: {context}
        Question: {question}
        Answer:"""
        
        # Get relevant documents
        docs = vector_store.similarity_search(question, k=3)
        context = "\n".join([doc.page_content for doc in docs])
        
        # Generate answer using new Gemini model
        prompt = prompt_template.format(context=context, question=question)
        response = model.generate_content(prompt)  # Changed client to model
        return response.text
    except Exception as e:
        st.error(f"Error generating answer: {str(e)}")
        return "Sorry, I couldn't generate an answer due to an error."

def main():
    st.title("PDF Knowledge Graph QA System")
    
    # File upload
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    
    if uploaded_file:
        # Extract text
        text = extract_text_from_pdf(uploaded_file)
        st.success("PDF processed successfully!")
        
        # Create KG button
        if st.button("Create Knowledge Graph"):
            with st.spinner("Creating Knowledge Graph..."):
                graph = process_text_for_kg(text)
                if graph:  # Only proceed if graph creation was successful
                    try:
                        vector_store = setup_vector_store()
                        st.session_state['graph'] = graph
                        st.session_state['vector_store'] = vector_store
                        st.success("Knowledge Graph created!")
                    except Exception as e:
                        st.error(f"Failed to setup vector store: {str(e)}")
        
        # QA section
        if 'graph' in st.session_state:
            st.subheader("Ask Questions")
            question = st.text_input("Enter your question:")
            
            if question:
                with st.spinner("Generating answer..."):
                    answer = answer_question(
                        question,
                        st.session_state['vector_store'],
                        st.session_state['graph']
                    )
                    st.write("Answer:", answer)

if __name__ == "__main__":
    st.set_page_config(page_title="PDF Knowledge Graph QA", layout="wide")
    main()
