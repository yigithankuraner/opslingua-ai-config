import os
import json
import logging
import requests
import copy
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from jsonschema import validate, ValidationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
SCHEMA_DIR = "/data/schemas"
VALUES_DIR = "/data/values"
MODEL_NAME = "llama3"

class MessageRequest(BaseModel):
    input: str

def get_file_content(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {filepath}")
        return None

def relax_schema_validation(schema_node):
    if isinstance(schema_node, dict):
        if "additionalProperties" in schema_node and schema_node["additionalProperties"] is False:
            schema_node["additionalProperties"] = True
        
        for key, value in schema_node.items():
            relax_schema_validation(value)
    elif isinstance(schema_node, list):
        for item in schema_node:
            relax_schema_validation(item)
    return schema_node

@app.post("/message")
async def process_message_jk(request: MessageRequest):
    logger.info(f"Received input: {request.input}")
    
    user_input = request.input.lower()
    target_app = None
    
    if "chat" in user_input:
        target_app = "chat"
    elif "matchmaking" in user_input:
        target_app = "matchmaking"
    elif "tournament" in user_input:
        target_app = "tournament"
    
    if not target_app:
        raise HTTPException(status_code=400, detail="Could not identify target app (chat/matchmaking/tournament).")

    schema_path = os.path.join(SCHEMA_DIR, f"{target_app}.schema.json")
    value_path = os.path.join(VALUES_DIR, f"{target_app}.value.json")
    
    schema_data = get_file_content(schema_path)
    value_data = get_file_content(value_path)
    
    if not schema_data or not value_data:
        raise HTTPException(status_code=500, detail=f"Failed to load data for {target_app}")

    prompt = f"""
    You are a DevOps assistant.
    
    Current Config (JSON):
    {json.dumps(value_data)}
    
    User Request: "{request.input}"
    
    CRITICAL RULES:
    1. The current JSON contains fields (like 'cronjobs', 'rollouts', 'statefulsets') that might NOT be in your schema knowledge.
    2. YOU MUST PRESERVE ALL UNKNOWN FIELDS EXACTLY AS THEY ARE. DO NOT DELETE THEM.
    3. ONLY modify the specific field requested by the user.
    4. Return ONLY the valid JSON.
    """

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "format": "json" 
            },
            timeout=120
        )
        response.raise_for_status()
        llm_result = response.json()
        new_config_str = llm_result.get("response", "")
        new_config = json.loads(new_config_str)
        
    except Exception as e:
        logger.error(f"LLM Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI Processing Failed: {str(e)}")

    try:
        schema_copy = copy.deepcopy(schema_data)
        relaxed_schema = relax_schema_validation(schema_copy)
        
        validate(instance=new_config, schema=relaxed_schema)
        logger.info("Validation Successful (Relaxed Mode)")
        
    except ValidationError as e:
        logger.error(f"Schema Validation Failed: {e.message}")
        raise HTTPException(status_code=500, detail=f"Schema Validation Failed: {e.message}")

    return new_config