# Text Embeddings

Embeddings answer the question: *"How can a computer understand the meaning of a word?"*


## What are Embeddings?

Embeddings are **lists of numbers** (vectors) that represent text.
*   Words with similar meanings have similar lists of numbers.
*   "King" and "Queen" will be closer mathematically than "King" and "Apple".

## Visual Analogy: The "Meaning" Space

Imagine a 2D graph where every word is a dot.
*   **"Dog"** is at coordinate `[1.2, 0.8]`
*   **"Puppy"** is at `[1.1, 0.9]` (Very close!)
*   **"Car"** is at `[9.5, -2.0]` (Far away)

Real embeddings use thousands of dimensions (e.g. 1536 for OpenAI's models), not just two!

## Mathematical Intuition: Cosine Similarity

To measure how similar two vectors are, we check the **angle** between them (Cosine Similarity).
*   **Same direction (0° angle)** = Similarity 1.0 (Exact match)
*   **Opposite direction (180° angle)** = Similarity -1.0 (Opposite meaning)
*   **90° angle** = Similarity 0.0 (Unrelated)

## Real-World Use Cases

### 1. Recommendation Systems (e.g., Netflix)
When you watch a sci-fi movie, Netflix converts that movie's description into an embedding. It then searches for other movies with **similar embeddings**.
*   "Interstellar" vector is close to "Gravity" vector.
*   "Interstellar" vector is far from "The Notebook" vector.

### 2. Semantic Search
Finding documents that match the *meaning* of a query, not just keywords.
*   Query: "Laptop battery dead"
*   Matches: "Computer power issues" (doesn't share words, but shares meaning!)
