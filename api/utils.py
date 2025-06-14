import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load course and discourse data
with open("data/discourse_posts.json", "r", encoding="utf-8") as f:
    discourse_data = json.load(f)

with open("data/course_content.json", "r", encoding="utf-8") as f:
    course_data = json.load(f)

# Combine data
combined_sources = discourse_data + course_data

def answer_question(question: str, image: str = None) -> tuple[str, list]:
    context = ""
    links = []

    # Basic keyword search for now
    for post in combined_sources:
        if question.lower() in post.get("content", "").lower():
            context += post["content"] + "\n"
            if post.get("link"):
                links.append(post["link"])

    if not context:
        context = "No exact matches found in the course or forum. Please try rephrasing your question."

    # Call OpenAI with context
    prompt = f"Answer the following question based only on this context:\n\n{context}\n\nQuestion: {question}\nAnswer:"
    
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful teaching assistant for an online data science course."},
            {"role": "user", "content": prompt}
        ]
    )

    answer = completion.choices[0].message.content.strip()
    return answer, links[:3]  # Return top 3 links
