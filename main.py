from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import json
from datetime import datetime

app = FastAPI(title="Animal & File API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnimalSelection(BaseModel):
    animal: str
    timestamp: Optional[str] = None

class FileInfo(BaseModel):
    filename: str
    size: int
    content_type: str
    timestamp: str

UPLOADS_DIR = "uploads"
DATA_FILE = "data.json"

if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"animals": [], "files": []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.get("/")
async def read_root():
    return FileResponse("index.html")

@app.get("/api")
async def api_root():
    return {"message": "Animal & File API is running"}

@app.post("/animal/select")
async def select_animal(selection: AnimalSelection):
    valid_animals = ["cat", "dog", "elephant"]
    
    if selection.animal not in valid_animals:
        raise HTTPException(status_code=400, detail="Invalid animal selection")
    
    data = load_data()
    
    animal_data = {
        "animal": selection.animal,
        "timestamp": datetime.now().isoformat()
    }
    
    data["animals"].append(animal_data)
    save_data(data)
    
    return {
        "message": f"{selection.animal.capitalize()} selected successfully",
        "data": animal_data
    }

@app.get("/animal/history")
async def get_animal_history():
    data = load_data()
    return {"history": data["animals"]}

@app.post("/file/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    
    file_path = os.path.join(UPLOADS_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    file_info = {
        "filename": file.filename,
        "size": len(content),
        "content_type": file.content_type or "unknown",
        "timestamp": datetime.now().isoformat(),
        "path": file_path
    }
    
    data = load_data()
    data["files"].append(file_info)
    save_data(data)
    
    return {
        "message": "File uploaded successfully",
        "file_info": {
            "name": file_info["filename"],
            "size": file_info["size"],
            "type": file_info["content_type"],
            "timestamp": file_info["timestamp"]
        }
    }

@app.get("/file/history")
async def get_file_history():
    data = load_data()
    return {"history": data["files"]}

@app.delete("/file/{filename}")
async def delete_file(filename: str):
    file_path = os.path.join(UPLOADS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    os.remove(file_path)
    
    data = load_data()
    data["files"] = [f for f in data["files"] if f["filename"] != filename]
    save_data(data)
    
    return {"message": f"File {filename} deleted successfully"}

@app.get("/stats")
async def get_stats():
    data = load_data()
    
    animal_counts = {}
    for animal_entry in data["animals"]:
        animal = animal_entry["animal"]
        animal_counts[animal] = animal_counts.get(animal, 0) + 1
    
    total_file_size = sum(f["size"] for f in data["files"])
    
    return {
        "total_animal_selections": len(data["animals"]),
        "animal_breakdown": animal_counts,
        "total_files_uploaded": len(data["files"]),
        "total_file_size_bytes": total_file_size
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)