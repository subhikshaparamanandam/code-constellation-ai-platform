# Retrieval-Augmented Generation (RAG)


Retrieval-Augmented Generation (RAG) is a technique that enhances Large Language Models (LLMs) by providing them with external data.

## key Concepts

1. **Retrieval**: Finding relevant information from a knowledge base (documents, databases) based on the user's query.
2. **Augmentation**: Adding the retrieved information to the prompt sent to the LLM.
3. **Generation**: The LLM generates a response using both its pre-trained knowledge and the specific retrieved information.

## detailed Explanation

Standard LLMs are trained on a vast amount of data, but that data is static. They don't know about private data or events that happened after their training cutoff.

RAG solves this by:
- Turning documents into *embeddings* (lists of numbers representing meaning).
- Storing these in a *vector database*.
- When a question is asked, the system searches for similar chunks of text in the database.
- These chunks are fed to the LLM as context.

## example Code (Conceptual)

```python
# Pseudo-code for RAG
query = "What is our company policy on remote work?"
relevant_docs = retrieve_documents(query)
prompt = f"Context: {relevant_docs}\n\nQuestion: {query}"
answer = llm.generate(prompt)
```
