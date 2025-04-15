from typing import List, Optional
from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, Field, field_serializer
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ]),
        ])
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return str(self.id)

class InternBase(BaseModel):
    name: str
    email: str

class InternCreate(InternBase):
    pass

class InternResponse(InternBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    
    class Config:
        validate_by_name = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
    
    @field_serializer('id')
    def serialize_id(self, id: PyObjectId) -> str:
        return str(id)

class AttendanceBase(BaseModel):
    intern_id: str
    date: str

class AttendanceCreate(BaseModel):
    intern_id: str

class AttendanceResponse(AttendanceBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    duration_minutes: Optional[float] = None
    
    class Config:
        validate_by_name = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
    
    @field_serializer('id')
    def serialize_id(self, id: PyObjectId) -> str:
        return str(id)

class TaskStatus(str, Enum):
    ASSIGNED = "assigned"
    COMPLETED = "completed"

class TaskBase(BaseModel):
    title: str
    assigned_to: str
    status: TaskStatus = TaskStatus.ASSIGNED

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    status: TaskStatus

class TaskResponse(TaskBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        validate_by_name = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
    
    @field_serializer('id')
    def serialize_id(self, id: PyObjectId) -> str:
        return str(id)