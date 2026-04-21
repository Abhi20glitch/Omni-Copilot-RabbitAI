"""
Memory router — CRUD for user memory entries.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# In-memory store (replace with Qdrant/DB in production)
_memories: list[dict] = []
_counter = 0


class MemoryEntry(BaseModel):
    key: str
    value: str


@router.get("/")
async def get_memories():
    """Fetch all memory entries."""
    return {"status": "ok", "memories": _memories}


@router.post("/")
async def add_memory(entry: MemoryEntry):
    """Add or update a memory entry."""
    global _counter
    # Check if key exists — update if so
    for mem in _memories:
        if mem["key"] == entry.key:
            mem["value"] = entry.value
            mem["updatedAt"] = datetime.now().isoformat()
            return {"status": "ok", "memory": mem, "action": "updated"}
    _counter += 1
    new_mem = {
        "id": str(_counter),
        "key": entry.key,
        "value": entry.value,
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    _memories.append(new_mem)
    return {"status": "ok", "memory": new_mem, "action": "created"}


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str):
    """Delete a memory entry by ID."""
    global _memories
    _memories = [m for m in _memories if m["id"] != memory_id]
    return {"status": "ok", "message": f"Memory {memory_id} deleted"}
