import os
from dotenv import load_dotenv
load_dotenv()
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_PROJECT"]=os.getenv("LANGCHAIN_PROJECT")
os.environ["TAVILY_API_KEY"]=os.getenv("TAVILY_API_KEY")
from langchain_groq import ChatGroq
model=ChatGroq(model="openai/gpt-oss-120b",temperature=0)

# model=ChatGroq(model="qwen/qwen3.6-27b",temperature=0)
# model=ChatGroq(model="llama-3.3-70b-versatile",temperature=0)
from langgraph.graph import StateGraph, START,END
from graph.schemas import State
from graph.nodes import fetch_trending_video,research_agent,finalize_youtube_content,generate_thumbnail,check_pipeline_status,log_error_message

print(model)

builder=StateGraph(State)

builder.add_node("fetch_trending_video",fetch_trending_video)
builder.add_node("research_agent",lambda state: research_agent(state,model))
builder.add_node("finalize_youtube_content",lambda state:finalize_youtube_content(state,model))
builder.add_node("generate_thumbnail",generate_thumbnail)
builder.add_node("log_error_message",log_error_message)

builder.add_edge(START, "fetch_trending_video")
builder.add_conditional_edges("fetch_trending_video",check_pipeline_status,{"continue":"research_agent",END:"log_error_message"})
# builder.add_edge("fetch_trending_video","research_agent")
# builder.add_edge("research_agent","finalize_youtube_content")
builder.add_conditional_edges("research_agent",check_pipeline_status,{"continue":"finalize_youtube_content",END:"log_error_message"})
# builder.add_edge("finalize_youtube_content","generate_thumbnail")
builder.add_conditional_edges("finalize_youtube_content",check_pipeline_status,{"continue":"generate_thumbnail",END:"log_error_message"})
builder.add_edge("generate_thumbnail",END)
builder.add_edge("log_error_message",END)
recommendation_graph=builder.compile()
# display(Image(graph.get_graph().draw_mermaid_png()))

# Testing block
if __name__ == "__main__":
    test_input = {"video_id": "test_123"}
    print("Running graph test...")
    output = recommendation_graph.invoke(test_input)
    print("\n--- Final Video Package ---")
    print(output.get("final_video_package"))