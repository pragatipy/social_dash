from typing import Optional

from ai_engine.chains import (
    llm,
    linkedin_post_chain,
    linkedin_article_chain,
    x_tweet_chain,
    x_thread_chain,
    refine_prompt,
)
from ai_engine.prompts import TONE_GUIDE, LENGTH_GUIDE

_PLATFORM_CHAINS = {
    "linkedin_post": linkedin_post_chain,
    "linkedin_article": linkedin_article_chain,
    "x_tweet": x_tweet_chain,
    "x_thread": x_thread_chain,
}

_PLATFORM_SCHEMAS = {
    "linkedin_post": linkedin_post_chain.last,    
    "linkedin_article": linkedin_article_chain.last,
    "x_tweet": x_tweet_chain.last,
    "x_thread": x_thread_chain.last,
}


def _brand_voice_block(brand_voice: Optional[str]) -> str:
    if not brand_voice:
        return ""
    return f"Brand voice profile to follow: {brand_voice}"


def generate(platform: str, topic: str, tone: str = "professional",
             length: str = "medium", brand_voice: Optional[str] = None):
    if platform not in _PLATFORM_CHAINS:
        raise ValueError(f"Unknown platform: {platform}")

    chain = _PLATFORM_CHAINS[platform]
    return chain.invoke({
        "topic": topic,
        "tone_desc": TONE_GUIDE[tone],
        "length_desc": LENGTH_GUIDE.get(length, LENGTH_GUIDE["medium"]),
        "brand_voice_block": _brand_voice_block(brand_voice),
    })


def refine(platform: str, draft, instruction: str):
    schema_cls = type(draft)  # reuse whatever schema the original draft used
    refine_chain = refine_prompt | llm.with_structured_output(schema_cls)
    return refine_chain.invoke({
        "draft": draft.model_dump_json(),
        "instruction": instruction,
    })