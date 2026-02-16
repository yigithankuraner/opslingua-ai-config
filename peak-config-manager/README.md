# Peak Config Manager - AI Powered DevOps Bot

A microservice-based application designed to manage Kubernetes configurations using Natural Language Processing (LLM). This system allows DevOps teams to modify complex JSON files through simple English commands while maintaining strict schema validation.

## 🚀 Features
* **AI-Powered:** Interprets user intent to modify JSON configurations via local LLM.
* **Resilient Architecture:** 3-tier microservices (Schema, Values, Bot) isolated via Docker Network.
* **Fail-Fast Validation:** Protects infrastructure by rejecting invalid AI outputs immediately before they reach the storage layer.
* **Data Integrity:** Specifically engineered to preserve unknown or legacy fields (e.g., `cronjobs`, `rollouts`) during updates.

## 🛠️ Prerequisites
* **Docker & Docker Compose**
* **Ollama** (Running on the host machine)
    * **Model:** `llama3`
    * **Setup:** Run `ollama pull llama3` before starting the services.

---

## 🏃‍♂️ How to Run (Step-by-Step)

### 1. Start Ollama (Host Machine)
To allow Docker containers to communicate with your local Ollama instance, start it with the following environment variable:

* **Windows (PowerShell):**
  ```powershell
  $env:OLLAMA_HOST="0.0.0.0"; ollama serve

* **Mac / Linux:**
Bash
OLLAMA_HOST=0.0.0.0 ollama serve

### 2. Start the Services
Navigate to the project's root directory and build/start the containers:

Bash
docker compose up --build

### How to Test
You can verify the system using two different methods.

## Option A: Automated Test (Recommended)
We have included a Python script that handles the request and displays the AI's response formatted:

Bash
python test_bot.py

## Option B: Manual Test (via Curl)
You can test specific scenarios requested in the project requirements:

# 1. Tournament Service (Set Memory):

Bash
curl -X POST http://localhost:5003/message \
     -H "Content-Type: application/json" \
     -d '{"input": "set tournament service memory to 1024mb"}'

# 2. Matchmaking Service (Set Env Variable):

Bash
curl -X POST http://localhost:5003/message \
     -H "Content-Type: application/json" \
     -d '{"input": "set GAME_NAME env to toyblast for matchmaking service"}'

# 3. Chat Service (Lower CPU Limit):

Bash
curl -X POST http://localhost:5003/message \
     -H "Content-Type: application/json" \
     -d '{"input": "lower cpu limit of chat service to %80"}'

### Service Ports

Service,      Port, Description
Schema Server,5001, Provides JSON Schemas for validation.
Values Server,5002, Stores and persists current configuration values.
Bot Server,   5003, The main entry point for AI processing and orchestration.

### Documentation & Architecture

For a deep dive into the Design Decisions, Architecture Diagrams, and Trade-offs (such as why we chose a Fail-Fast strategy over a Retry Loop), please refer to the INTERN.md file included in this repository.

