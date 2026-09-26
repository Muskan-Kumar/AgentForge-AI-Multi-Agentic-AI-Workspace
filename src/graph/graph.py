from langgraph.graph import START, END, StateGraph
from langchain_core.messages import ToolMessage, HumanMessage

from src.agents.chat_agent import chat_agent
from src.agents.coding_agent import coding_agent
from src.agents.search_agent import search_agent
from src.agents.pdf_agent import pdf_agent
from src.agents.image_agent import image_agent
from src.agents.ppt_agent import ppt_agent

from src.graph.supervisor import supervisor_select_agents
from src.graph.final_response import final_response_node
from src.graph.context import build_agent_messages

from src.memory.long_term_memory import long_term_memory
from src.memory.memory_extractor import extract_and_save_memories

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
import logging

logger = logging.getLogger(__name__)




def extract_artifact_path(result: str) -> str:
    if not result:
        return ""

    for line in result.splitlines():
        line = line.strip()

        if line.startswith("File:"):
            return line.replace("File:", "", 1).strip()

    return ""


##--- chat node----
# def chat_node(state: AgentState) -> dict:

#     response = chat_agent.invoke(
#         {
#             "messages": build_agent_messages(
#                 state,
#                 "chat",
#             )
#         }
#     )

#     return {
#         "messages": [response],
#         "chat_result": response.content,
#         "current_agent_index": (
#             state.get("current_agent_index", 0) + 1
#         ),
#     }

def chat_node(state: AgentState) -> dict:
    logger.info("Chat agent started")

    user_query = state.get("user_query", "")

    response = chat_agent.invoke(
        {
            "messages": build_agent_messages(
                state,
                "chat",
            )
        }
    )

    logger.info("Chat agent completed")

    agents_executed = list(
        state.get(
            "agents_executed",
            [],
        )
    )

    if "chat" not in agents_executed:
        agents_executed.append("chat")

    return {
        "messages": [
            HumanMessage(
                content=user_query
            ),
            response,
        ],
        "chat_result": response.content,
        "agents_executed": agents_executed,
        "execution_status": "running",
        "current_agent_index": (
            state.get(
                "current_agent_index",
                0,
            ) + 1
        ),
    }



##---coding node-----
def coding_node(state: AgentState)-> dict:
    logger.info("Coding agent started")

    response = coding_agent.invoke(
        {
            "messages": build_agent_messages(state, "coding")
        }
    )

    logger.info("Coding agent completed")

    agents_executed = list(
        state.get(
            "agents_executed",
            [],
        )
    )

    if "coding" not in agents_executed:
        agents_executed.append("coding")

    result = {
        "messages": [response],
        "agents_executed": agents_executed,
        "execution_status": "running",
    }

    if not response.tool_calls:
        result["coding_result"] = response.content
        result["current_agent_index"] = (
            state.get("current_agent_index", 0) + 1
        )

    return result



##---search node----
def search_node(state: AgentState)->dict:
    logger.info("Search agent started")

    response = search_agent.invoke(
        {
            "messages": build_agent_messages(state, "search")
        }
    )

    logger.info("Search agent completed")

    agents_executed = list(
        state.get(
            "agents_executed",
            [],
        )
    )

    if "search" not in agents_executed:
        agents_executed.append("search")


    result = {
        "messages": [response],
        "agents_executed": agents_executed,
        "execution_status": "running",
    }

    if not response.tool_calls:
        result["search_results"] = response.content
        result["current_agent_index"] = (
            state.get("current_agent_index", 0) + 1
        )

    return result


##---pdf node----
def pdf_node(state: AgentState)->dict:
    logger.info("Pdf agent started")

    response = pdf_agent.invoke(
        {
            "messages": build_agent_messages(state, "pdf")
        }
    )

    logger.info("Pdf agent completed")

    agents_executed = list(
        state.get(
            "agents_executed",
            [],
        )
    )

    if "pdf" not in agents_executed:
        agents_executed.append("pdf")

    result = {
        "messages": [response],
        "agents_executed": agents_executed,
        "execution_status": "running",
    }

    if not response.tool_calls:
        result["pdf_context"] = response.content
        result["current_agent_index"] = (
            state.get("current_agent_index", 0) + 1
        )

    return result



##----- image node-----
def image_node(state: AgentState) -> dict:
    messages = state.get("messages", [])

    if messages and isinstance(messages[-1], ToolMessage):
        image_result = messages[-1].content
        image_file = extract_artifact_path(image_result)


        logger.info("Image agent completed | file=%s",image_file,)


        agents_executed = list(
            state.get(
                "agents_executed",
                [],
            )
        )

        return {
            "image_file": image_file,
            "agents_executed": agents_executed,
            "execution_status": "running",
            "current_agent_index": (
                state.get("current_agent_index", 0) + 1
            ),
        }

    logger.info("Image agent started")

    response = image_agent.invoke(
        {
            "messages": build_agent_messages(
                state,
                "image"
            )
        }
    )


    agents_executed = list(
        state.get(
            "agents_executed",
            [],
        )
    )

    if "image" not in agents_executed:
        agents_executed.append("image")

    return {
        "messages": [response],
        "agents_executed": agents_executed,
        "execution_status": "running",
    }


##-----ppt node----
def ppt_node(state: AgentState) -> dict:
    messages = state.get("messages", [])

    if messages and isinstance(messages[-1], ToolMessage):
        ppt_result = messages[-1].content
        ppt_file = extract_artifact_path(ppt_result)


        logger.info("PPT agent completed | file=%s",ppt_file,)

        agents_executed = list(
            state.get(
                "agents_executed",
                [],
            )
        )

        return {
            "ppt_result": ppt_result,
            "ppt_file": ppt_file,
            "agents_executed": agents_executed,
            "execution_status": "running",
            "current_agent_index": (
                state.get("current_agent_index", 0) + 1
            ),
        }

    logger.info("PPT agent started")

    response = ppt_agent.invoke(
        {
            "messages": build_agent_messages(
                state,
                "ppt"
            )
        }
    )


    agents_executed = list(
        state.get(
            "agents_executed",
            [],
        )
    )

    if "ppt" not in agents_executed:
        agents_executed.append("ppt")

    
    return {
        "messages": [response],
        "agents_executed": agents_executed,
        "execution_status": "running",
    }



def load_long_term_memory(state: AgentState) -> dict:

    user_id = state.get("thread_id")
    user_query = state.get("user_query", "")

    if not user_id or not user_query:
        return {}

    memories = long_term_memory.get_relevant_memories(
        user_id=user_id,
        query=user_query,
    )

    if not memories:
        return {}

    memory_context = "\n".join(
        f"{key}: {value}"
        for key, value in memories.items()
    )

    return {
        "memory_context": memory_context
    }



###-----multi agent prepare node-----
def prepare_agent_execution(state: AgentState) -> dict:
    agent_mode = state.get("agent_mode", "chat")

    if agent_mode == "auto":
        selected_agents = supervisor_select_agents(
            state.get("user_query", "")
        )
    else:
        selected_agents = [agent_mode]

    logger.info(
        "Agent execution started | mode=%s | agents=%s",
        agent_mode,
        selected_agents,
    )

    return {
        "selected_agents": selected_agents,
        "current_agent_index": 0,
        "agents_executed": [],
        "execution_status": "running",
    }


##--- next agent node(dusre agent ko access krne ke liye. ex-> search agento -> ppt agent)
def next_agent_node(state: AgentState) -> dict:
    return {}


def save_long_term_memory(state: AgentState) -> dict:

    user_id = state.get("thread_id")
    user_query = state.get("user_query", "")

    if not user_id or not user_query:
        return {}

    extract_and_save_memories(
        user_id=user_id,
        conversation=user_query,
    )

    return {}



## --- graph build ----
def build_graph(checkpointer):
    workflow = StateGraph(AgentState)

    ##--core node--
    workflow.add_node("prepare_execution",prepare_agent_execution)
    workflow.add_node("load_memory", load_long_term_memory)
    workflow.add_node("next_agent",next_agent_node)
    workflow.add_node("final_response", final_response_node)
    workflow.add_node("save_memory", save_long_term_memory)


    ##--agent node---
    workflow.add_node("chat", chat_node)
    workflow.add_node("coding", coding_node)
    workflow.add_node("search", search_node)
    workflow.add_node("pdf",pdf_node)
    workflow.add_node("image",image_node)
    workflow.add_node("ppt",ppt_node)

    ##--tool node--
    workflow.add_node("coding_tools", coding_tool_node)
    workflow.add_node("search_tools",search_tool_node)
    workflow.add_node("pdf_tools",pdf_tool_node)
    workflow.add_node("image_tools",image_tool_node)
    workflow.add_node("ppt_tools",ppt_tool_node)

    ##--start--
    workflow.add_edge(START, "load_memory")
    workflow.add_edge("load_memory", "prepare_execution")

     #--Initial agent routing--
    workflow.add_conditional_edges("prepare_execution", route_agent,{
        "chat": "chat",
        "coding": "coding",
        "search": "search",
        "pdf": "pdf",
        "image": "image",
        "ppt":"ppt",
    },)

    ##--chat--
    workflow.add_conditional_edges("chat", route_next_agent,{
        "coding": "coding",
        "search": "search",
        "pdf": "pdf",
        "image": "image",
        "ppt": "ppt",
        "end": "final_response",
    },)

    ##--codding--
    workflow.add_conditional_edges("coding",route_coding_tools,{
        "tools":"coding_tools",
        "end":"next_agent",
    })
    workflow.add_edge("coding_tools", "coding")

    ##--search--
    workflow.add_conditional_edges("search",route_search_tools,{
        "tools":"search_tools",
        "end":"next_agent",
    })
    workflow.add_edge("search_tools", "search")

    #---pdf---
    workflow.add_conditional_edges("pdf",route_pdf_tools,{
        "tools":"pdf_tools",
        "end":"next_agent",
    })
    workflow.add_edge("pdf_tools", "pdf")

    ##--image---
    workflow.add_conditional_edges("image",route_image_tools,{
        "tools": "image_tools",
        "end": "next_agent",
    },)
    workflow.add_edge("image_tools", "image")

    ##---ppt---
    workflow.add_conditional_edges("ppt",route_ppt_tools,{
        "tools": "ppt_tools",
        "end": "next_agent",
    },)
    workflow.add_edge("ppt_tools", "ppt")

    ##--next agent routing---
    workflow.add_conditional_edges("next_agent",route_next_agent,{
        "chat": "chat",
        "coding": "coding",
        "search": "search",
        "pdf": "pdf",
        "image": "image",
        "ppt": "ppt",
        "end": "final_response",
    })

    workflow.add_edge("final_response", "save_memory")
    workflow.add_edge("save_memory", END)

    return workflow.compile(
    checkpointer=checkpointer
)



