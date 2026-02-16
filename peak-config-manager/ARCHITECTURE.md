# Engineering Internship Project: Design & Architecture Report

## 🎯 1. Project Philosophy
This project was designed not just as a functional tool, but as a **resilient microservice architecture** capable of handling the non-deterministic nature of Large Language Models (LLMs) within a strict DevOps environment.

My primary goal was to bridge the gap between "AI probability" and "Infrastructure reliability."

---

## 🏗️ 2. System Architecture & Communication

The system follows a strict **Microservices Architecture** pattern. Communication is handled via synchronous HTTP REST calls.

### Architecture Diagram
The following diagram illustrates the data flow and the **Fail-Fast Validation Strategy** (Rendered via Mermaid):

```mermaid
graph TD
    User["User / Client"] -- "HTTP POST" --> BotService["🤖 Bot Service"]

    subgraph Docker Network
        BotService -- "GET /schemas" --> SchemaService["📄 Schema Service"]
        BotService -- "GET /values" --> ValuesService["💾 Values Service"]

        BotService -. "POST /api/generate" .-> Ollama["🧠 Ollama (Local LLM)"]
        Ollama -. "JSON Response" .-> BotService

        BotService -- Validate --> Validation{"Valid?"}
        
        %% Success Path %%
        Validation -- "Yes" --> Update["PUT /values (Persist)"]
        Update --> ValuesService
        
        %% Fail-Fast Path %%
        Validation -- "No" --> Error["❌ Halt & Return HTTP 500"]
    end

    ValuesService -- "Read/Write" --- Volume["📂 Docker Volume"]

🚀 Component Structure  

    Schema Service (Port 5001): Acts as the immutable registry for validation rules.

    Values Service (Port 5002): Manages the state (Single Source of Truth) for configurations.

    Bot Service (Port 5003): The orchestrator. It handles logic, AI inference, and validation.

🔄 3. End-to-End Request Flow
Matches Requirement: "The end-to-end flow of a user request"

When a user sends the request: "change chat maxUser to 50"

Intent Analysis: The Bot Service identifies the target application (chat).

Context Loading: Fetches current state (values.json) and rules (schema.json).

AI Inference: A specialized prompt injects the current JSON and user request.

Runtime Validation (Critical Step): The AI-generated JSON is validated against the schema.

Persistence: Only valid configurations are written to disk.

💡 4. Design Decisions & Trade-offs (Reasoning)
Matches Requirement: "Focus on reasoning and trade-offs"

## A. Choice of LLM: Llama3 (via Ollama)
Decision: I chose llama3 running locally via Ollama instead of a cloud API (like OpenAI).

Reasoning:

Privacy: DevOps configurations often contain sensitive data; keeping inference local prevents data leaks.

Cost: Eliminates API costs completely.

Reliability: Llama3 8B is currently the state-of-the-art for instruction following in smaller parameter models.

## B. "Fail-Fast" vs. "Auto-Retry" Strategy
Decision: If validation fails, the system returns an error immediately (HTTP 500) instead of asking the AI to retry.

Trade-off:

Alternative: Trying to fix the JSON automatically (Auto-Retry).

Why Rejected: Infinite loops with non-deterministic LLMs can lead to "hallucinations" or data corruption.

Verdict: In infrastructure management, predictability is safer than probability. It is better to halt than to apply a guessed configuration.

## C. Validation Strategy: The "Unknown Fields" Problem
Challenge: Real-world production data contained fields (e.g., rollouts) that were missing from the strict schema.json.

Decision: Implemented a Runtime Schema Relaxation algorithm in Python.

Reasoning: Modifying the "Source of Truth" (Schema files) was risky. Adapting the validation logic allowed the system to handle legacy data gracefully without breaking strict type checks for the modified fields.