from langgraph.prebuilt import ToolNode
from src.tools.web_search_tool import web_search
from src.tools.pdf_tool import pdf_tool
from src.tools.rag_tool import rag_tool
from src.tools.image_tool import image_tool
from src.tools.ppt_tool import ppt_tool
from src.tools.code_execution_tool import code_execution_tool


## ----tool node----
search_tool_node = ToolNode([web_search])
pdf_tool_node = ToolNode([pdf_tool, rag_tool])
image_tool_node = ToolNode([image_tool])
ppt_tool_node = ToolNode([ppt_tool])
coding_tool_node = ToolNode([code_execution_tool])
