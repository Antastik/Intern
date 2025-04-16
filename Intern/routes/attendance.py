from fastapi import APIRouter, HTTPException, Body
from typing import List
from datetime import datetime
from bson.objectid import ObjectId
from models import AttendanceCreate, AttendanceResponse
from database import attendance_collection, interns_collection

router = APIRouter()

def attendance_helper(attendance) -> dict:
    return {
        "id": attendance["_id"],  
        "intern_id": attendance["intern_id"],
        "date": attendance["date"],
        "check_in": attendance.get("check_in"),
        "check_out": attendance.get("check_out"),
        "duration_minutes": attendance.get("duration_minutes")
    }

@router.post("/check-in", response_model=AttendanceResponse)
def check_in(attendance: AttendanceCreate = Body(...)):
    try:
        if not interns_collection.find_one({"_id": ObjectId(attendance.intern_id)}):
            raise HTTPException(status_code=404, detail=f"Intern with ID {attendance.intern_id} not found")
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        existing_attendance = attendance_collection.find_one({
            "intern_id": attendance.intern_id,
            "date": current_date
        })
        
        if existing_attendance:
            if "check_in" in existing_attendance:
                raise HTTPException(status_code=400, detail="Already checked in for today")
            
            current_time = datetime.now().strftime("%H:%M:%S")
            attendance_collection.update_one(
                {"_id": existing_attendance["_id"]},
                {"$set": {"check_in": current_time}}
            )
            
            updated_attendance = attendance_collection.find_one({"_id": existing_attendance["_id"]})
            return attendance_helper(updated_attendance)
        else:
            current_time = datetime.now().strftime("%H:%M:%S")
            attendance_dict = {
                "intern_id": attendance.intern_id,
                "date": current_date,
                "check_in": current_time
            }
            
            result = attendance_collection.insert_one(attendance_dict)
            created_attendance = attendance_collection.find_one({"_id": result.inserted_id})
            return attendance_helper(created_attendance)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")

@router.post("/check-out", response_model=AttendanceResponse)
def check_out(attendance: AttendanceCreate = Body(...)):
    try:
        if not interns_collection.find_one({"_id": ObjectId(attendance.intern_id)}):
            raise HTTPException(status_code=404, detail=f"Intern with ID {attendance.intern_id} not found")
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        existing_attendance = attendance_collection.find_one({
            "intern_id": attendance.intern_id,
            "date": current_date
        })
        
        if not existing_attendance:
            raise HTTPException(status_code=404, detail="No check-in record found for today")
        
        if "check_out" in existing_attendance:
            raise HTTPException(status_code=400, detail="Already checked out for today")
        
        if "check_in" not in existing_attendance:
            raise HTTPException(status_code=400, detail="Must check in before checking out")
        
        current_time = datetime.now().strftime("%H:%M:%S")
        check_in_time = datetime.strptime(existing_attendance["check_in"], "%H:%M:%S")
        check_out_time = datetime.strptime(current_time, "%H:%M:%S")
        
        duration = (check_out_time - check_in_time).total_seconds() / 60
        
        attendance_collection.update_one(
            {"_id": existing_attendance["_id"]},
            {"$set": {
                "check_out": current_time,
                "duration_minutes": duration
            }}
        )
        
        updated_attendance = attendance_collection.find_one({"_id": existing_attendance["_id"]})
        return attendance_helper(updated_attendance)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")

@router.get("/", response_model=List[AttendanceResponse])
def get_all_attendance():
    attendance_records = []
    for record in attendance_collection.find():
        attendance_records.append(attendance_helper(record))
    return attendance_records

@router.get("/intern/{intern_id}", response_model=List[AttendanceResponse])
def get_intern_attendance(intern_id: str):
    try:
        if not interns_collection.find_one({"_id": ObjectId(intern_id)}):
            raise HTTPException(status_code=404, detail=f"Intern with ID {intern_id} not found")
        
        attendance_records = []
        for record in attendance_collection.find({"intern_id": intern_id}):
            attendance_records.append(attendance_helper(record))
        
        return attendance_records
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format or request: {str(e)}")