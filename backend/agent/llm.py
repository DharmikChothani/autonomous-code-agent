import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# ----------------------------------------------------
# Primary LLM: Google Gemini
# ----------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
)

# ----------------------------------------------------
# Secondary LLM: Groq
# ----------------------------------------------------

llm2 = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=1,
    max_tokens=2048,
    top_p=1,
    reasoning_effort="medium",
    api_key=os.getenv("GROQ_API_KEY"),
)