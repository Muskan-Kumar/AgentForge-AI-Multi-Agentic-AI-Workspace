from langgraph.graph import START, END, StateGraph

from src.agents.chat_agent import chat_agent
from src.agents.coding_agent import coding_agent
from src.agents.search_agent import search_agent
from src.agents.pdf_agent import pdf_agent

from src.graph.router import route_agent, route_search_tools, route_pdf_tools

from src.graph.tool_nodes import search_tool_node,pdf_tool_node

from src.state.agent_state import AgentState




##--- chat node----
def chat_node(state: AgentState)->dict:
    response = chat_agent.invoke(
        {
            "input": state["user_query"]
        }
    )

    return {
        "message": [response],
        "chat_results": response.content,
        "final_response": response.content,
    }


##---coding node-----
def coding_node(state: AgentState)-> dict:
    response = coding_agent.invoke(
        {
            "input": state["user_query"]
        }
    )

    return {
        "message":[response],
        "coding_results":response.content,
        "final_response":response.content,
    }



##---search node----
def serch_node(state: AgentState)->dict:
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

    return result




## --- graph build ----
def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("chat", chat_node)
    workflow.add_node("coding", coding_node)
    workflow.add_node("search", serch_node)
    workflow.add_node("search_tools",search_tool_node)
    workflow.add_node("pdf",pdf_node)
    workflow.add_node("pdf_tools",pdf_tool_node)


    workflow.add_conditional_edges(START, route_agent,{
        "chat": "chat",
        "coding": "coding",
        "search": "search",
        "pdf": "pdf",
    },)

    workflow.add_edge("chat", END)
    workflow.add_edge("coding", END)
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


    return workflow.compile()



agentforge_graph = build_graph()