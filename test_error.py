import sys
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import get_tools

try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key="dummy")
    create_react_agent(model=llm, tools=get_tools(), messages_modifier="test")
except Exception as e:
    with open("err.log", "w") as f:
        f.write(str(e))
