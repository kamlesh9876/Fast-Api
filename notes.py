from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn
import os

app = FastAPI(
    title="Notes API",
    description="Backend for Notes Application",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- MODELS ----------------

class Note(BaseModel):
    id: int
    title: str
    content: str
    tags: List[str]
    created_at: datetime

class NoteCreate(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

# ---------------- DATABASE ----------------

notes_db: List[dict] = []
next_id = 1

# ---------------- ROUTES ----------------

@app.get("/")
def root():
    return {"message": "Notes API running 🚀"}

@app.post("/notes", response_model=Note)
def create_note(note: NoteCreate):
    global next_id

    new_note = {
        "id": next_id,
        "title": note.title,
        "content": note.content,
        "tags": note.tags or [],
        "created_at": datetime.now()
    }
    notes_db.append(new_note)
    next_id += 1
    return new_note

@app.get("/notes", response_model=List[Note])
def get_notes(
    search: Optional[str] = Query(None),
    tag: Optional[str] = Query(None)
):
    results = notes_db

    if search:
        results = [
            n for n in results
            if search.lower() in n["title"].lower()
            or search.lower() in n["content"].lower()
        ]

    if tag:
        results = [
            n for n in results
            if tag.lower() in [t.lower() for t in n["tags"]]
        ]

    return results

@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int):
    note = next((n for n in notes_db if n["id"] == note_id), None)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, note: NoteUpdate):
    for n in notes_db:
        if n["id"] == note_id:
            if note.title is not None:
                n["title"] = note.title
            if note.content is not None:
                n["content"] = note.content
            if note.tags is not None:
                n["tags"] = note.tags
            return n

    raise HTTPException(status_code=404, detail="Note not found")

@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    for i, n in enumerate(notes_db):
        if n["id"] == note_id:
            notes_db.pop(i)
            return {"message": "Note deleted successfully"}

    raise HTTPException(status_code=404, detail="Note not found")

# ---------------- RUN ----------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))  # different port
    uvicorn.run("notes:app", host="0.0.0.0", port=port, reload=True)
