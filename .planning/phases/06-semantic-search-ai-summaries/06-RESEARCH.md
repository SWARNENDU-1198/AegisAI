# Phase 6: Semantic Search & AI Summaries - Research

## 1. Gemini Embedding Generation
We will use `genai.embed_content` with model `"models/text-embedding-004"`.

For files (documents):
```python
response = genai.embed_content(
    model="models/text-embedding-004",
    content=document_text,
    task_type="retrieval_document"
)
embedding = response["embedding"]
```

For search queries:
```python
response = genai.embed_content(
    model="models/text-embedding-004",
    content=query_text,
    task_type="retrieval_query"
)
embedding = response["embedding"]
```

## 2. Cosine Similarity Calculation
We will calculate cosine similarity natively in Python:
```python
import math

def cosine_similarity(v1, v2):
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)
```

## 3. Folder Summary Prompt Construction
To summarize a folder, we gather its database records and construct a summary description prompt for `gemini-2.5-flash`:
```python
# Prompt structure
prompt = f"""
You are AegisAI, an intelligent Digital Intelligence Assistant for Windows.
Summarize the contents of the directory: '{directory_path}'.
Here is the context of the files located in this directory:
- Total file count: {total_count}
- Total size: {total_size_bytes} bytes
- Files list:
{files_list_text}

Provide a short, professional, and friendly summary of this folder. Describe what kind of folder this is (e.g. Code workspace, Pictures, Documents) based on the categories, list key documents/media files, point out any security warnings (like plain-text passwords or scripts), and suggest any cleanup optimization tips (like duplicates).
"""
```
