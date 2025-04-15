from fastapi import APIRouter, HTTPException, Body, Query
from typing import List
from bson.objectid import ObjectId
from models import TaskCreate, TaskResponse, TaskUpdate, TaskStatus
from database import tasks_collection, interns_collection

router = APIRouter()

def task_helper(task) -> dict:
    return {
        "id": task["_id"],  
        "title": task["title"],
        "assigned_to": task["assigned_to"],
        "status": task["status"]
    }

@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate = Body(...), role: str = Query(..., description="User role (admin/intern)")):
    if role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Only admins can assign tasks")
    
    try:
        if not interns_collection.find_one({"_id": ObjectId(task.assigned_to)}):
            raise HTTPException(status_code=404, detail=f"Intern with ID {task.assigned_to} not found")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid intern ID format")
    
    task_dict = task.model_dump()  
    result = tasks_collection.insert_one(task_dict)
    
    created_task = tasks_collection.find_one({"_id": result.inserted_id})
    return task_helper(created_task)

@router.get("/", response_model=List[TaskResponse])
def get_all_tasks():
    tasks = []
    for task in tasks_collection.find():
        tasks.append(task_helper(task))
    return tasks

@router.get("/intern/{intern_id}", response_model=List[TaskResponse])
def get_intern_tasks(intern_id: str):
    try:
        if not interns_collection.find_one({"_id": ObjectId(intern_id)}):
            raise HTTPException(status_code=404, detail=f"Intern with ID {intern_id} not found")
        
        tasks = []
        for task in tasks_collection.find({"assigned_to": intern_id}):
            tasks.append(task_helper(task))
        
        return tasks
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format or request: {str(e)}")

@router.put("/{task_id}", response_model=TaskResponse)
def update_task_status(
    task_id: str, 
    task_update: TaskUpdate = Body(...), 
    role: str = Query(..., description="User role (admin/intern)"),
    user_id: str = Query(..., description="ID of the user making the request")
):
    try:
        task = tasks_collection.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
        
        if task_update.status == TaskStatus.COMPLETED:
            if role.lower() != "intern":
                raise HTTPException(status_code=403, detail="Only interns can complete tasks")
            
            if task["assigned_to"] != user_id:
                raise HTTPException(status_code=403, detail="Interns can only complete tasks assigned to them")
        
        tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {"status": task_update.status}}
        )
        
        updated_task = tasks_collection.find_one({"_id": ObjectId(task_id)})
        return task_helper(updated_task)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Invalid ID format or request: {str(e)}")

@router.delete("/{task_id}")
def delete_task(task_id: str, role: str = Query(..., description="User role (admin/intern)")):
    if role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete tasks")
    
    try:
        delete_result = tasks_collection.delete_one({"_id": ObjectId(task_id)})
        
        if delete_result.deleted_count == 1:
            return {"status": "success", "message": f"Task with ID {task_id} deleted"}
            
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format or request: {str(e)}")