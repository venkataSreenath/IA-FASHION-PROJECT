from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import get_tools

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key="dummy")
tools = get_tools()

success = []

def try_kwarg(kwarg_name):
    try:
        kwargs = {"model": llm, "tools": tools, kwarg_name: "test"}
        create_react_agent(**kwargs)
        success.append(kwarg_name)
    except Exception as e:
        pass

try_kwarg("state_modifier")
try_kwarg("messages_modifier")
try_kwarg("system_prompt")
try_kwarg("system_message")

with open("kwarg_test.log", "w") as f:
    f.write("Success keywords: " + str(success))
