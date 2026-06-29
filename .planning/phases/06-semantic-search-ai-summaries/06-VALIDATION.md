# Phase 6: Semantic Search & AI Summaries - Validation

## Testing Plan

We will create a test suite `backend/test_semantic_search.py` covering:

1. **Unit Tests for Vector Operations**:
   - Check `cosine_similarity()` with identical, orthogonal, and opposite vectors.
   - Verify handling of empty/zero vectors.

2. **Unit Tests for Embedding Generation**:
   - Verify text representation formatter output for different file types.
   - Mock the Gemini embedding API to return fake 768-dimensional float lists and verify correct handling.

3. **Integration Tests**:
   - Verify background scanning correctly generates embeddings and saves them in the database.
   - Verify GET `/semantic-search` returns files sorted by descending similarity matches.
   - Verify GET `/folder-summary` builds prompt and returns Gemini output successfully.
