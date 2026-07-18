from typing import List
from pydantic import BaseModel, Field, field_validator


class LinkedInPostDraft(BaseModel):
    content: str = Field(description="Full LinkedIn post, following hook -> value -> CTA structure")
    hashtags: List[str] = Field(description="3-5 relevant hashtags, without the # symbol")


class ArticleSection(BaseModel):
    heading: str = Field(description="Section heading")
    content: str = Field(description="Section body text")


class LinkedInArticleDraft(BaseModel):
    title: str = Field(description="Compelling article title")
    sections: List[ArticleSection] = Field(description="Structured body sections")
    conclusion: str = Field(description="Closing paragraph / CTA")
    hashtags: List[str] = Field(description="3-5 relevant hashtags, without the # symbol")

    @field_validator("hashtags")
    @classmethod
    def strip_hash_symbol(cls, v: List[str]) -> List[str]:
        return [tag.lstrip("#") for tag in v]


class XTweetDraft(BaseModel):
    content: str = Field(description="A single tweet, must stay under 280 characters")
    hashtags: List[str] = Field(description="1-3 relevant hashtags, without the # symbol")

    @field_validator("hashtags")
    @classmethod
    def strip_hash_symbol(cls, v: List[str]) -> List[str]:
        return [tag.lstrip("#") for tag in v]

    @field_validator("content")
    @classmethod
    def enforce_char_limit(cls, v: str) -> str:
        if len(v) > 280:
            raise ValueError(f"Tweet exceeds 280 characters ({len(v)} chars)")
        return v


class XThreadDraft(BaseModel):
    tweets: List[str] = Field(description="Ordered tweets forming the thread, each under 280 characters")
    hashtags: List[str] = Field(description="1-3 relevant hashtags, without the # symbol")

    @field_validator("hashtags")
    @classmethod
    def strip_hash_symbol(cls, v: List[str]) -> List[str]:
        return [tag.lstrip("#") for tag in v]

    @field_validator("tweets")
    @classmethod
    def enforce_char_limit(cls, v: List[str]) -> List[str]:
        for i, tweet in enumerate(v):
            if len(tweet) > 280:
                raise ValueError(f"Tweet {i+1} exceeds 280 characters ({len(tweet)} chars)")
        return v