from fastapi import APIRouter, HTTPException, status
from typing import List
from models import InternCreate, InternResponse
from database import interns_collection
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=InternResponse, status_code=status.HTTP_201_CREATED)
async def create_intern(intern: InternCreate):
    new_intern = intern.dict()
    result = interns_collection.insert_one(new_intern)
    created_intern = interns_collection.find_one({"_id": result.inserted_id})
    return created_intern

@router.get("/", response_model=List[InternResponse])
async def get_interns():
    interns = list(interns_collection.find())
    return interns

@router.get("/{intern_id}", response_model=InternResponse)
async def get_intern(intern_id: str):
    if not ObjectId.is_valid(intern_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    intern = interns_collection.find_one({"_id": ObjectId(intern_id)})
    if intern is None:
        raise HTTPException(status_code=404, detail="Intern not found")
    return intern

@router.delete("/{intern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_intern(intern_id: str):
    if not ObjectId.is_valid(intern_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    result = interns_collection.delete_one({"_id": ObjectId(intern_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Intern not found")









