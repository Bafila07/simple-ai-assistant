# AI Agent Learnings

## 1. Avoiding Tool Over-Reliance

### Problem

The agent refused to answer general questions when no tool was relevant.

**Example:**  
For the question, “What is data streaming?”, the agent said it could not answer because no tool was available.

### Cause

The system prompt did not clearly state that the agent could use its own knowledge.

### Solution

The system prompt now distinguishes between:

- **General questions:** Answer using the model’s knowledge.
- **Live or external information:** Use an appropriate tool.
- **No relevant tool:** Answer directly instead of refusing.

### System Prompt

> You are a helpful AI assistant.  
> Answer general questions using your own knowledge.  
> Use tools only when relevant or necessary.  
> Do not refuse a question simply because no tool is available.  
> Answer clearly and briefly.

### Result

The agent can now:

- Answer general questions directly.
- Use tools when external or live information is needed.
- Treat tools as additional capabilities, not limitations.

### Key Learning

Tools extend an agent’s capabilities; they should not restrict what it can answer.


## 2. Streaming Responses

### Problem

The agent waited for the complete response before displaying anything, making it feel slow.

### Cause

The response was generated and returned all at once instead of being streamed in chunks.

### Solution

Enable streaming with `stream=True` and print each received chunk immediately.

### Result

The agent now displays responses progressively, making it feel faster and more like ChatGPT.

### Key Learning

Streaming improves responsiveness by showing partial output while the model continues generating the rest of the response.

## 3. Streaming Tool Calls

### Problem

Tool calls arrive in multiple streamed fragments instead of one complete object.

### Solution

Collect fragments using their index, then combine the tool name and arguments before executing the tool.

### Result

The agent can process streamed tool calls correctly while maintaining their order.

### Key Learning

Streamed tool calls must be reconstructed completely before execution.


## 4. Embeddings and Semantic Search

### Embeddings

Embeddings convert text into numerical vectors that represent its meaning.

This project uses the `nomic-embed-text:latest` embedding model.

### Semantic Search

Semantic search finds text based on meaning rather than exact keyword matches. This allows related questions and documents to match even when they use different words.

### Cosine Similarity

Cosine similarity measures how similar two embedding vectors are by comparing the angle between them.

- A score close to `1` means highly similar meanings.
- A score close to `0` means little or no similarity.
- A negative score indicates opposing directions.

### Key Learning

Embeddings represent meaning, semantic search finds meaningful matches, and cosine similarity ranks those matches by similarity.

## 5. Document Search with Embeddings

### Problem

The application needed to search documents based on their meaning instead of relying only on exact keyword matches.

### Solution

The document search system uses embeddings and cosine similarity:

1. Load text files from the knowledge-base folder.
2. Generate an embedding for each document using `nomic-embed-text:latest`.
3. Generate an embedding for the user’s query.
4. Compare the query embedding with each document embedding.
5. Rank documents by similarity score.
6. Return the top matching documents.

### Key Learnings

- Documents and user queries can be converted into numerical vectors called embeddings.
- The `nomic-embed-text:latest` model generates embeddings for both documents and queries.
- Semantic search finds relevant content based on meaning, not just matching keywords.
- Cosine similarity measures how closely two embeddings are related.
- Higher cosine similarity scores indicate greater semantic similarity.
- Documents can be ranked by their similarity scores to return the most relevant results.
- Embeddings allow the agent to search a knowledge base more intelligently.

