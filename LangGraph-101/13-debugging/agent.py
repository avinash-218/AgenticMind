import os
from typing import Annotated, TypedDict
from langgraph.graph import START, add_messages, StateGraph
from langchain_core.messages import BaseMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
load_dotenv()

os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
os.environ['LANGSMITH_API_KEY'] = os.getenv('LANGSMITH_API_KEY')
os.environ['LANGSMITH_TRACING'] = os.getenv('LANGSMITH_TRACING')
os.environ['LANGSMITH_PROJECT'] = os.getenv('LANGSMITH_PROJECT')

llm = init_chat_model("groq:llama-3.1-8b-instant")

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def make_tool_graph():
    @tool
    def add(a:float, b:float)->float:
        """Add two numbers"""
        return a+b
    
    tools = [add]
    llm_with_tools = llm.bind_tools(tools=tools)

    def call_llm_model(state:State):
        return {"messages":[llm_with_tools.invoke(state["messages"])]}
    
    builder = StateGraph(State)
    builder.add_node("tool_calling_llm", call_llm_model)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "tool_calling_llm")
    builder.add_conditional_edges(
        "tool_calling_llm",
        tools_condition
    )
    builder.add_edge("tools", "tool_calling_llm")

    graph = builder.compile()
    return graph

tool_agent = make_tool_graph()