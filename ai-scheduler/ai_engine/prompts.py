from langchain_core.prompts import ChatPromptTemplate

TONE_GUIDE = {
    "professional": "polished, credible, and business-appropriate",
    "casual": "relaxed, conversational, and approachable",
    "bold": "confident, direct, and attention-grabbing",
    "storytelling": "narrative-driven, built around a small story or anecdote",
}

LENGTH_GUIDE = {
    "short": "brief and punchy",
    "medium": "a few short paragraphs",
    "long": "detailed and thorough",
}

LINKEDIN_POST_SYSTEM = """You are an expert LinkedIn content writer.
Write posts that follow a hook -> value -> call-to-action structure.
Tone: {tone_desc}
Length: {length_desc}
{brand_voice_block}"""

LINKEDIN_ARTICLE_SYSTEM = """You are an expert LinkedIn long-form article writer.
Write a structured article: compelling title, clear headed sections, strong conclusion.
Tone: {tone_desc}
Length: {length_desc}
{brand_voice_block}"""

X_TWEET_SYSTEM = """You are an expert X (Twitter) copywriter.
Write one punchy tweet, strictly under 280 characters.
Tone: {tone_desc}
{brand_voice_block}"""

X_THREAD_SYSTEM = """You are an expert X (Twitter) thread writer.
Write a multi-tweet thread; each tweet must stay under 280 characters.
Tone: {tone_desc}
Length: {length_desc}
{brand_voice_block}"""

REFINE_SYSTEM = """You are refining existing social media content.
Apply the user's instruction precisely while preserving the original intent and platform constraints.
Return the FULL revised content in the same structure, not just the changed part."""


def build_generation_prompt(system_template: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", "Topic: {topic}"),
    ])


def build_refine_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", REFINE_SYSTEM),
        ("human", "Original content:\n{draft}\n\nInstruction: {instruction}"),
    ])