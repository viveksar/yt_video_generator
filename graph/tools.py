import os
from dotenv import load_dotenv
load_dotenv()
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from pydantic import BaseModel,Field



# tavily_search = TavilySearch(
#     max_results=2,
#     topic="news"
# )
# @tool
# def tavily_search_tool(query: str):
#     """
#     Search the web for current and recent information.
#     Use this tool when up-to-date information from the internet is required.
#     Args:
#         query: A specific web search query describing exactly what information
#                you need to find is requried.
#     """
#     print("Tavily search query:", query)
#     if not query.strip():
#         return "No search query was provided."
#     result = tavily_search.invoke(query)
#     print("Tavily result:", result)
#     return result

class SearchInput(BaseModel):
    query: str = Field(
        ..., 
        description="The clean search string or keywords to search the web for. Do not include URLs or pagination parameters."
    )

@tool(args_schema=SearchInput)
def tavily_search_tool(query: str) -> str:
    """Performs a live web search for news and facts based on a keyword search query."""
    search_tool = TavilySearch(
        max_results=2,
        topic="news",
        tavily_api_key=os.getenv("TAVILY_API_KEY")
    )
    return search_tool.invoke(query)

@tool
def generate_thumb_image(title:str,description:str|None=''):
    """This tool generates the thumbnail image from the title and description of the video."""
    print("here is title and description to generate thumb image:",title)
    return "https://image/"+"_".join(title[:10])