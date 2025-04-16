from fastapi import APIRouter, HTTPException, Body
from typing import List
from bson.objectid import ObjectId
from models import InternCreate, InternResponse
from database import interns_collection

router = APIRouter()

def intern_helper(intern) -> dict:
    return {
        "id": intern["_id"],  
        "name": intern["name"],
        "email": intern["email"]
    }

@router.post("/", response_model=InternResponse)
def create_intern(intern: InternCreate = Body(...)):
    intern_dict = intern.model_dump() 
    result = interns_collection.insert_one(intern_dict)
    
    created_intern = interns_collection.find_one({"_id": result.inserted_id})
    return intern_helper(created_intern)

@router.get("/", response_model=List[InternResponse])
def get_all_interns():
    interns = []
    for intern in interns_collection.find():
        interns.append(intern_helper(intern))
    return interns

@router.get("/{intern_id}", response_model=InternResponse)
def get_intern(intern_id: str):
    try:
        intern = interns_collection.find_one({"_id": ObjectId(intern_id)})
        if intern:
            return intern_helper(intern)
        raise HTTPException(status_code=404, detail=f"Intern with ID {intern_id} not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format or request: {str(e)}")

@router.delete("/{intern_id}")
def delete_intern(intern_id: str):
    try:
        delete_result = interns_collection.delete_one({"_id": ObjectId(intern_id)})
        
        if delete_result.deleted_count == 1:
            return {"status": "success", "message": f"Intern with ID {intern_id} deleted"}
            
        raise HTTPException(status_code=404, detail=f"Intern with ID {intern_id} not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format or request: {str(e)}")