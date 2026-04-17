from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import get_tools

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key="dummy")
tools = get_tools()

results = {}

def try_kwarg(kwarg_name):
    try:
        kwargs = {"model": llm, "tools": tools}
        if kwarg_name:
            kwargs[kwarg_name] = "test"
        create_react_agent(**kwargs)
        results[kwarg_name or "NONE"] = "SUCCESS"
    except Exception as e:
        results[kwarg_name or "NONE"] = str(e)

try_kwarg(None)
try_kwarg("state_modifier")
try_kwarg("messages_modifier")
try_kwarg("system_message")
try_kwarg("prompt")

with open("kwarg_test2.log", "w") as f:
    import json
    json.dump(results, f, indent=4)
