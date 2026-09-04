from langchain_tavily import TavilySearch
from langchain_core.tools import tool


tavily_search = TavilySearch(
    max_results=2,
    topic="news"
)
@tool
def tavily_search_tool(query: str):
    """
    Search the web for current and recent information.
    Use this tool when up-to-date information from the internet is required.
    Args:
        query: A specific web search query describing exactly what information
               you need to find.
    """
    print("Tavily search query:", query)
    if not query.strip():
        return "No search query was provided."
    result = tavily_search.invoke(query)
    print("Tavily result:", result)
    return result

@tool
def generate_thumb_image(title:str,description:str|None=''):
    """This tool generates the thumbnail image from the title and description of the video."""
    print("here is title and description to generate thumb image:",title)
    return "https://image/"+"_".join(title[:10])