from langgraph.graph import START, END, StateGraph

from src.agents.chat_agent import chat_agent
from src.agents.coding_agent import coding_agent
from src.agents.search_agent import search_agent
from src.agents.pdf_agent import pdf_agent
from src.graph.router import route_agent
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
            "input":state["user_query"]
        }
    )

    return {
            "message":[response],
            "search_results":response.content,
            "final_response":response.content,
        }


##---pdf node----
def pdf_node(state: AgentState)->dict:
    response = pdf_agent.invoke(
        {
            "input": state["user_query"]
        }
    )

    return {
            "message":[response],
            "pdf_results":response.content,
            "final_response":response.content,
        }




## --- graph build ----
def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("chat", chat_node)
    workflow.add_node("coding", coding_node)
    workflow.add_node("search", serch_node)
    workflow.add_node("pdf",pdf_node)

    workflow.add_conditional_edges(START, route_agent,{
        "chat": "chat",
        "coding": "coding",
        "search": "search",
        "pdf": "pdf",
    })

    workflow.add_edge("chat", END)
    workflow.add_edge("coding", END)
    workflow.add_edge("search", END)
    workflow.add_edge("pdf", END)


    return workflow.compile()



agentforge_graph = build_graph()