from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from typing import Optional,Dict
class ReleventVideo(BaseModel):
    """Structure of an individual relevant video idea."""

    title: str = Field(
        description="Engaging, clickable, and search-optimized title."
    )
    summary: str = Field(
        description="2-3 sentence overview of the core concept and content flow."
    )
    viewer_hook: str = Field(
        description="Why the reference video viewer would click this."
    )
    relevancy_score: float = Field(
        description="Relevancy score compared to the reference video from 0.0 to 1.0."
    )


class ReleventVideos(BaseModel):
    """Container for the list of generated video ideas."""

    videos: list[ReleventVideo] = Field(
        description="List containing exactly 1 relevant video ideas.",
        min_length=1,
        max_length=1,
    )

class RawVideoInput(BaseModel):
    title: str
    summary: str
    viewer_hook: str


class GeneratedVideoData(BaseModel):
    title: str = Field(
        description="High-CTR, curiosity-driven YouTube title under 65 characters without clickbait violation."
    )
    description: str = Field(
        description="SEO-optimized description containing an engaging 2-3-sentence hook, video summary, structured timestamps/key takeaways, and relevant hashtags."
    )
    tags: list[str] = Field(
        description="10 to 15 targeted keywords combining broad reach, niche tags, and long-tail search queries."
    )

class CombineVideoData(GeneratedVideoData):
    thumb_image:str=Field(description="It contains the thumb url of the video")

class ReferenceVideo(BaseModel):
    title:str=Field(description="contains title of the video")
    description:str=Field(description="contains the description of the videos")
    channelTitle:str=Field(description="It is the title of youtube channel")
    tags:list[str]|str|None=Field(description="It contains the list of tags related to video")
    
class State(TypedDict):
    video_id:str
    refrence_video:ReferenceVideo
    relevent_videos:ReleventVideos
    final_video_data:GeneratedVideoData
    final_video_package:CombineVideoData
    status:str
    error_message:Optional[Dict[str,str]]