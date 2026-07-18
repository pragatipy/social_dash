from langchain_google_genai import ChatGoogleGenerativeAI

from ai_engine.schemas import LinkedInPostDraft, LinkedInArticleDraft, XTweetDraft, XThreadDraft
from ai_engine.prompts import (
    build_generation_prompt,
    build_refine_prompt,
    LINKEDIN_POST_SYSTEM,
    LINKEDIN_ARTICLE_SYSTEM,
    X_TWEET_SYSTEM,
    X_THREAD_SYSTEM,
)

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")

linkedin_post_chain = build_generation_prompt(LINKEDIN_POST_SYSTEM) | llm.with_structured_output(LinkedInPostDraft)
linkedin_article_chain = build_generation_prompt(LINKEDIN_ARTICLE_SYSTEM) | llm.with_structured_output(LinkedInArticleDraft)
x_tweet_chain = build_generation_prompt(X_TWEET_SYSTEM) | llm.with_structured_output(XTweetDraft)
x_thread_chain = build_generation_prompt(X_THREAD_SYSTEM) | llm.with_structured_output(XThreadDraft)

refine_prompt = build_refine_prompt()