from langgraph.prebuilt import ToolNode
from src.tools.web_search_tool import web_search
from src.tools.pdf_tool import pdf_tool
from src.tools.rag_tool import rag_tool


## ----tool node----
search_tool_node = ToolNode([web_search])
pdf_tool_node = ToolNode([pdf_tool, rag_tool])
