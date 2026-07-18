# test_generator.py
from dotenv import load_dotenv
load_dotenv()

from generator import generate, refine

article = generate(
    platform="linkedin_article",
    topic="Why interns should ship real features, not toy projects",
    tone="professional",
    length="long",
    brand_voice="Direct, no-fluff, occasionally sarcastic. Avoids corporate buzzwords.",
)
print("Title:", article.title)
for section in article.sections:
    print(f"\n## {section.heading}\n{section.content}")
print("\nConclusion:", article.conclusion)
print("Hashtags:", article.hashtags)