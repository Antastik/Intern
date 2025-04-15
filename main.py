from fastapi import FastAPI
import uvicorn
import pymongo
import datetime
from routes import interns, attendance, tasks

app = FastAPI()

app.include_router(interns.router, prefix="/api/interns", tags=["Interns"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])

@app.get("/")
def root():
    return {"message": "welcome to Intern Management System"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)