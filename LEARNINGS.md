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