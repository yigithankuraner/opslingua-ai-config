import os
import json
from fastapi import FastAPI, HTTPException

app = FastAPI()

VALUES_DIR = "/data/values"

@app.get("/{app_name}")
def get_values(app_name: str):
    file_path = os.path.join(VALUES_DIR, f"{app_name}.value.json")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Values not found")

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))