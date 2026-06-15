from ai.gemini import ask_ai

from services.storage_service import (
    get_storage_analysis,
    get_largest_files
)

from services.duplicate_service import (
    find_duplicates
)


def answer_question(question):

    storage = get_storage_analysis()

    largest = get_largest_files(10)

    duplicates = find_duplicates()

    prompt = f"""
You are AegisAI.

You are analyzing a user's computer.

Storage Analysis:
{storage}

Largest Files:
{largest}

Duplicates:
{duplicates}

User Question:
{question}

Answer clearly and professionally.
Do not make up information.
Only use provided data.
"""

    return ask_ai(prompt)