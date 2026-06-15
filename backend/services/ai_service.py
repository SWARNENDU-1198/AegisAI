from ai.gemini import ask_ai

from services.storage_service import (
    get_storage_analysis,
    get_largest_files
)

from services.duplicate_service import (
    find_duplicates
)


def generate_cleanup_advice():

    storage = get_storage_analysis()

    largest = get_largest_files()

    duplicates = find_duplicates()

    prompt = f"""
You are AegisAI.

Analyze this storage data.

Storage:
{storage}

Largest Files:
{largest}

Duplicates:
{duplicates}

Provide:

1. Storage health assessment
2. Cleanup recommendations
3. Estimated risks
4. Priority actions
"""

    return ask_ai(prompt)