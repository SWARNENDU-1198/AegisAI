import os

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def ask_ai(prompt):

    try:

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:

        return f"AI Error: {str(e)}"


import logging
logger = logging.getLogger(__name__)

def get_embedding(text: str, is_query: bool = False) -> list[float]:
    task_type = "retrieval_query" if is_query else "retrieval_document"
    try:
        response = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text,
            task_type=task_type
        )
        return response.get("embedding", [])
    except Exception as e:
        logger.error("Failed to generate embedding: %s", str(e))
        return []