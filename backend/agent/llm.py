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
    # or "gemini-1.5-flash" / "gemini-2.0-flash" depending on your API support
  
)

# ----------------------------------------------------
# Secondary LLM
# ----------------------------------------------------


llm2 = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=1,
    max_tokens=2048,
    top_p=1,
    reasoning_effort="medium",  # Passed directly as a top-level parameter
    api_key=os.getenv("GROQ_API_KEY"),
)
