from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["intern_management"]

interns_collection = db["interns"]
attendance_collection = db["attendance"]
tasks_collection = db["tasks"]