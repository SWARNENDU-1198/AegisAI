from ai.gemini import ask_ai, get_embedding
from services.semantic_service import cosine_similarity
from database.db import SessionLocal
from database.models import FileRecord
import json

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
    
    # Semantic Search Context
    semantic_results = []
    if get_embedding:
        query_emb = get_embedding(question, is_query=True)
        if query_emb:
            db = SessionLocal()
            try:
                records = db.query(FileRecord).filter(FileRecord.vector_embedding.isnot(None)).all()
                scored_files = []
                for r in records:
                    try:
                        emb = json.loads(r.vector_embedding)
                        if emb:
                            score = cosine_similarity(query_emb, emb)
                            scored_files.append((score, r))
                    except Exception:
                        continue
                # Sort by score desc, take top 5
                scored_files.sort(key=lambda x: x[0], reverse=True)
                for score, r in scored_files[:5]:
                    semantic_results.append(
                        f"- {r.name} (Path: {r.path}, Category: {r.category}, Size: {r.size} bytes, Similarity: {score:.3f})"
                    )
            finally:
                db.close()

    semantic_context = "\n".join(semantic_results) if semantic_results else "No semantically matching files found."

    prompt = f"""
You are AegisAI.

You are analyzing a user's computer.

Storage Analysis:
{storage}

Largest Files:
{largest}

Duplicates:
{duplicates}

Semantically Matching Files (based on User Question):
{semantic_context}

User Question:
{question}

Answer clearly and professionally.
Do not make up information.
Only use provided data.
"""

    return ask_ai(prompt)