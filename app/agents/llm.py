from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def generate_reply(prompt: str):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a strict JSON generator for a support system."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
    )

    return response.choices[0].message.content