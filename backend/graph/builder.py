# alfred/backend/graph/builder.py

from .state import State
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from graph.nodes.router_node import router_node
from graph.nodes.alfred_node import alfred_node
from graph.nodes.memory_node import memory_node, memory_tools
from graph.nodes.task_node import task_node, task_tools
from graph.nodes.weather_node import weather_node, weather_tools

builder = StateGraph(State)

builder.add_node("router_node", router_node)
builder.add_node("alfred_node", alfred_node)

builder.add_node("memory_node", memory_node)
builder.add_node("memory_tool_node", ToolNode(memory_tools))

builder.add_node("task_node", task_node)
builder.add_node("task_tool_node", ToolNode(task_tools))

builder.add_node("weather_node", weather_node)
builder.add_node("weather_tool_node", ToolNode(weather_tools))

builder.add_conditional_edges(
    "router_node",
    lambda state: state.get("next"),
    {"alfred_node": "alfred_node", 
     "memory_node": "memory_node",
     "task_node": "task_node",
     "weather_node": "weather_node",}
)

builder.add_edge(START, "router_node")
builder.add_edge("memory_node", "memory_tool_node")
builder.add_edge("memory_tool_node", "alfred_node")

builder.add_edge("task_node", "task_tool_node")
builder.add_edge("task_tool_node", "alfred_node")

builder.add_edge("weather_node", "weather_tool_node")
builder.add_edge("weather_tool_node", "alfred_node")

builder.add_edge("alfred_node", END)

graph = builder.compile()