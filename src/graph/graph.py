from langgraph.graph import START, END, StateGraph

from src.agents.chat_agent import chat_agent
from src.agents.coding_agent import coding_agent
from src.agents.search_agent import search_agent
from src.agents.pdf_agent import pdf_agent
from src.agents.image_agent import image_agent
from src.agents.ppt_agent import ppt_agent

from src.graph.supervisor import supervisor_select_agents

from src.graph.router import (
    route_agent, 
    route_search_tools, 
    route_pdf_tools,
    route_image_tools,
    route_ppt_tools,
    route_coding_tools,
    route_next_agent,
)

from src.graph.tool_nodes import (
    search_tool_node,
    pdf_tool_node,
    image_tool_node,
    ppt_tool_node,
    coding_tool_node,
)

from src.state.agent_state import AgentState




##--- chat node----
def chat_node(state: AgentState)->dict:
    response = chat_agent.invoke(
        {
            "input": state["user_query"]
        }
    )

    return {
        "messages": [response],
        "chat_result": response.content,
        "final_response": response.content,
        "current_agent_index": state.get(
            "current_agent_index",0
        ) + 1,
    }


##---coding node-----
def coding_node(state: AgentState)-> dict:
    response = coding_agent.invoke(
        {
            "messages": state.get("messages",[])
        }
    )

    result = {
        "messages": [response],
    }

    if not response.tool_calls:
        result["coding_result"] = response.content
        result["final_response"] = response.content
        result["current_agent_index"] = (
            state.get("current_agent_index", 0) + 1
        )

    return result



##---search node----
def search_node(state: AgentState)->dict:
    response = search_agent.invoke(
        {
            "messages": state.get("messages",[])
        }
    )

    result = {
        "messages": [response],
    }

    if not response.tool_calls:
        result["search_results"] = response.content
        result["final_response"] = response.content
        result["current_agent_index"] = (
            state.get("current_agent_index", 0) + 1
        )

    return result


##---pdf node----
def pdf_node(state: AgentState)->dict:
    response = pdf_agent.invoke(
        {
            "messages": state.get("messages", [])
        }
    )

    result = {
        "messages": [response],
    }

    if not response.tool_calls:
        result["pdf_context"] = response.content
        result["final_response"] = response.content
        result["current_agent_index"] = (
            state.get("current_agent_index", 0) + 1
        )

    return result



##----- image node-----
def image_node(state: AgentState)->dict:
    response = image_agent.invoke(
        {
            "messages": state.get("messages",[])
        }
    )

    result = {
        "messages": [response],
    }

    if not response.tool_calls:
        result["image_file"] = response.content
        result["final_response"] = response.content
        result["current_agent_index"] = (
            state.get("current_agent_index", 0) + 1
        )

    return result


##-----ppt node----
def ppt_node(state: AgentState)->dict:
    response = ppt_agent.invoke(
        {
            "messages": state.get("messages",[])
        }
    )

    result = {
        "messages": [response],
    }

    if not response.tool_calls:
        result["ppt_result"] = response.content
        result["final_response"] = response.content
        result["current_agent_index"] = (
            state.get("current_agent_index", 0) + 1
        )

    return result



###-----multi agent prepare node-----
def prepare_agent_execution(state: AgentState) -> dict:
    agent_mode = state.get("agent_mode", "chat")

    if agent_mode == "auto":
        selected_agents = state.get("selected_agents")

        if not selected_agents:
            selected_agents = supervisor_select_agents(
                state.get("user_query", "")
            )

        return {
            "selected_agents": selected_agents,
            "current_agent_index": 0,
        }

    return {
        "selected_agents": [agent_mode],
        "current_agent_index": 0,
    }


##--- helper function for increment current agnt index
def advance_agent(state: AgentState) -> dict:
    return {
        "current_agent_index": state.get(
            "current_agent_index",
            0
        ) + 1
    }


## --- graph build ----
def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("prepare_execution",prepare_agent_execution)

    workflow.add_node("chat", chat_node)

    workflow.add_node("coding", coding_node)
    workflow.add_node("coding_tools", coding_tool_node)

    workflow.add_node("search", search_node)
    workflow.add_node("search_tools",search_tool_node)

    workflow.add_node("pdf",pdf_node)
    workflow.add_node("pdf_tools",pdf_tool_node)

    workflow.add_node("image",image_node)
    workflow.add_node("image_tools",image_tool_node)

    workflow.add_node("ppt",ppt_node)
    workflow.add_node("ppt_tools",ppt_tool_node)


    workflow.add_edge(START, "prepare_execution")

    workflow.add_conditional_edges("prepare_execution", route_agent,{
        "chat": "chat",
        "coding": "coding",
        "search": "search",
        "pdf": "pdf",
        "image": "image",
        "ppt":"ppt",
    },)


    workflow.add_conditional_edges("chat", route_next_agent,{
        "coding": "coding",
        "search": "search",
        "pdf": "pdf",
        "image": "image",
        "ppt": "ppt",
        "end": END,
    },)

    workflow.add_conditional_edges("coding",route_coding_tools,{
        "tools":"coding_tools",
        "end":END,
    })
    workflow.add_edge("coding_tools", "coding")

    workflow.add_conditional_edges("search",route_search_tools,{
        "tools":"search_tools",
        "end":END,
    })
    workflow.add_edge("search_tools", "search")
    
    workflow.add_conditional_edges("pdf",route_pdf_tools,{
        "tools":"pdf_tools",
        "end":END,
    })
    workflow.add_edge("pdf_tools", "pdf")

    workflow.add_conditional_edges("image",route_image_tools,{
        "tools": "image_tools",
        "end": END,
    },)
    workflow.add_edge("image_tools", "image")

    workflow.add_conditional_edges("ppt",route_ppt_tools,{
        "tools": "ppt_tools",
        "end": END,
    },)
    workflow.add_edge("ppt_tools", "ppt")


    return workflow.compile()



agentforge_graph = build_graph()
