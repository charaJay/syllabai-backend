import os
from openai import OpenAI

MODEL = "gpt-5.1"

def get_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key)

def extract_topics(api_key: str, text: str) -> list[str]:
    client = get_client(api_key)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that extracts topics from academic syllabi."
            },
            {
                "role": "user",
                "content": f"Extract the main topics from this syllabus as a concise bullet point list. Return only the topic names, one per line, no extra text or formatting:\n\n{text}"
            }
        ]
    )
    raw = response.choices[0].message.content
    topics = [line.strip("•-– ").strip() for line in raw.strip().splitlines() if line.strip()]
    return topics


def stream_chat(api_key: str, messages: list[dict]):
    client = get_client(api_key)
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True
    )

def generate_checklist(api_key: str, topic: str) -> list[dict]:
    client = get_client(api_key)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful academic tutor creating concise learning checklists."
            },
            {
                "role": "user",
                "content": f"Create a short learning checklist for the topic '{topic}'. Return 4-6 items maximum. Return only the checklist items, one per line, no bullets, no numbers, no extra text."
            }
        ]
    )
    raw = response.choices[0].message.content
    items = [line.strip() for line in raw.strip().splitlines() if line.strip()]
    return [{"text": item, "done": False} for item in items]