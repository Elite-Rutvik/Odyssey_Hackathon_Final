import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from langchain_core.messages.ai import AIMessage

# Load environment variables from .env.local file
load_dotenv('.env.local')

# Get API keys from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Initialize Groq with API key explicitly
groq_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY
)

system_prompt = "Act as an AI chatbot who is smart and friendly"
search_tool = TavilySearchResults(
    max_results=2,
    tavily_api_key=TAVILY_API_KEY
)
agent = create_react_agent(
    model=groq_llm,
    tools=[search_tool],
    state_modifier = system_prompt
)

query = "Tell me about trend in Crypto markets"
state = {"messages":query}
response = agent.invoke(state)
messages = response.get("messages")
ai_messages = [message.content for message in messages if isinstance(message, AIMessage)]
print(ai_messages[-1])