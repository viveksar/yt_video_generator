from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from graph.prompts import RESEARCH_AGENT_SYSTEM_MESSAGE, RESEARCH_AGENT_SYSTEM_MESSAGE_TO_STRUCTURE,FINAL_YOUTUBE_CONTENT_SYSTEM_PROMPT, FINAL_YOUTUBE_CONTENT_HUMAN_PROMPT
from langgraph.graph import END
from datetime import datetime
from graph.tools import tavily_search_tool,generate_thumb_image
from graph.schemas import  ReleventVideos,GeneratedVideoData

def fetch_trending_video(state):
    try:
        video_id=state["video_id"]
        print("fetch trending video node called")
        # res= requests.get("https://abcd.com/")
        # data=res.json()
        # This is the data of that trending video
        data={
            "title":"US Iran War: ईरान पर अमेरिका की ताबड़तोड़ कार्रवाई! ट्रंप बोले- रडार और नौसैनिक ढांचा तबाह | AajTak",
            "channelTitle":"Aajtak",
            "tags":["usiranwar" ,"usattack ","trump ","atwebvideos ","aajtak  ","aajtakdigital" ,"tvchunks"],
            "description":"""ईरान और अमेरिका के बीच तनाव लगातार बढ़ता जा रहा है। अमेरिकी राष्ट्रपति डोनाल्ड ट्रंप ने दावा किया है कि अमेरिकी सेना ने ईरान के रडार और नौसैनिक ढांचे पर बेहद भारी हमले किए हैं। वहीं ईरान की ओर से अमेरिकी हमलों में एक शादी समारोह को निशाना बनाए जाने और बड़ी संख्या में लोगों के हताहत होने का दावा किया गया है।

    इस बीच ईरान ने अमेरिकी MQ-9 रीपर ड्रोन को मार गिराने का दावा किया है। आर्थिक मोर्चे पर भी दबाव बढ़ रहा है, जबकि SCO सम्मेलन के दौरान पीएम मोदी और ईरानी राष्ट्रपति मसूद पेज़ेश्कियान की मुलाकात के बाद अमेरिका की ओर से ईरान की आर्थिक मदद या प्रतिबंधों को दरकिनार करने वाले देशों को चेतावनी दी गई है। आखिर ईरान-अमेरिका की इस जंग का अगला मोड़ क्या होगा? 
    """
            

        }
        required_data={}
        required_data["title"]=data["title"]
        required_data["description"]=data["description"]
        required_data["channelTitle"]=data["channelTitle"]
        required_data["tags"]=data["tags"]
        print("result of fetch trending vide node:",required_data)
        return {"refrence_video":required_data}
    except Exception as ex:
        print("here is the error in fetch_trending_video:",ex)
        return {"status":"failed","error_message":{"node":"fetch_trending_video","message":str(ex)}}
                

def research_agent(state,model):
    try:
        """Researches trending updates and returns 1 validated, structured video concepts."""
        refrence_video = state["refrence_video"]
        current_date=datetime.now()

        # 1. Agent System Prompt: Guides web search & analysis
        agent_system_message = RESEARCH_AGENT_SYSTEM_MESSAGE.format(
            current_date=current_date,
            refrence_video_title=refrence_video.get("title", ""),
            refrence_video_channel_title=refrence_video.get("channelTitle", ""),
            refrence_video_description=refrence_video.get("description", ""),
            refrence_video_tags=refrence_video.get("tags", "")
            )
        agent = create_agent(
            model=model,
            tools=[tavily_search_tool],
            system_prompt=agent_system_message,
        )
        print("here agent decleration ended and agent invocation happen")
        agent_res = agent.invoke({
            "messages": [{
                "role": "user", 
                "content": "Research the latest facts and real-time updates for this video topic. Formulate 1 distinct video angles.",
                
            }]
        })
        print("here agent invocation has ended")
        agent_message = agent_res["messages"][-1].content

        # 2. Structured Output Prompt: Injects the agent's verified research

        structured_output_prompt = ChatPromptTemplate.from_messages([
            ("system", RESEARCH_AGENT_SYSTEM_MESSAGE_TO_STRUCTURE),
            (
                "human",
                """Below is the verified research report on this topic:

    ---
    {research_data}
    ---

    Generate the 1 structured video concept based on this verified research."""
            ),
        ])

        model_with_structured_output = model.with_structured_output(ReleventVideos)
        chain = structured_output_prompt | model_with_structured_output

        # 3. Invoke chain with reference metadata and research data
        result = chain.invoke({
            "ref_title": refrence_video.get("title", ""),
            "ref_channel": refrence_video.get("channelTitle", ""),
            "ref_desc": refrence_video.get("description", ""),
            "research_data": agent_message,
        })
        return {"relevent_videos":result.videos}
    except Exception as ex:
            print("here is exception in research_agent:",ex)
            return {"status":"failed","error_message":{"node":"research_agent","message":str(ex)}}


def finalize_youtube_content(state,model):
    try:
        relevent_videos=state["relevent_videos"]
        inputs=[{"title":video.title if hasattr(video,"title") else video["title"],
                "summary":video.summary if hasattr(video,"summary") else video["summary"],
                "viewer_hook":video.viewer_hook if hasattr(video,"viewer_hook") else video["viewer_hook"]
                } for video in relevent_videos]

        prompt = ChatPromptTemplate.from_messages([
            ("system", FINAL_YOUTUBE_CONTENT_SYSTEM_PROMPT),
            ("human", FINAL_YOUTUBE_CONTENT_HUMAN_PROMPT),
        ])
        structured_model = model.with_structured_output(GeneratedVideoData)
        chain = prompt | structured_model
        final_video_data=chain.batch(inputs)
        print("here is the final_video data:",final_video_data)
        # return final_video_data
        return {"final_video_data":final_video_data}
    except Exception as ex:
        print("here is exception in finalize_youtube_content:",ex)
        return {"status":"failed","error_message":{"node":"finalize_youtube_content","message":str(ex)}}

def generate_thumbnail(state):
    try:
        final_video_data=state["final_video_data"]
        inputs=[{"title":video.title,"description":video.description} for video in final_video_data]
        thumbnails=generate_thumb_image.batch(inputs)
        print("here are all the thumbnails==>",thumbnails)
        combined_videos = [
            {
                **video.model_dump(),     # Unpacks title, description, tags, etc.
                "thumb_image": thumb      # Adds the thumbnail result
            }
            for video, thumb in zip(final_video_data, thumbnails)
        ]
        
        print("Combined video package:", combined_videos)
        return {"final_video_package": combined_videos}
    except Exception as ex:
        print("here is exception in generate_thumbnail:",ex)
        return {"status":"failed","error_message":{"node":"generate_thumbnail","message":str(ex)}}

def check_pipeline_status(state):
    """Route the graph to End if any node generate error"""
    if state.get("status")=="failed":
        return END
    return "continue"

def log_error_message(state):
    """This node is responsible to print error message if any"""
    if state.get("status")=="failed":
        print("Error in Node:",state.get("error_message")["node"])
        print("Error message:",state.get("error_message")["message"])