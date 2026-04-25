from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

# ✅ CORS FIX (important)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FILE = "students.json"


def read_data():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r") as f:
        return json.load(f)


def write_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


# CREATE
@app.post("/students")
def create_student(student: dict):
    data = read_data()

    new_id = max([s["id"] for s in data], default=0) + 1

    student_obj = {
        "id": new_id,
        "name": student.get("name"),
        "age": student.get("age"),
        "deleted": False
    }

    data.append(student_obj)
    write_data(data)
    return student_obj


# READ with filters
@app.get("/students")
def get_students(
    name: str = Query(None),
    show_deleted: bool = False
):
    data = read_data()

    result = []
    for s in data:
        if not show_deleted and s["deleted"]:
            continue
        if name and name.lower() not in s["name"].lower():
            continue
        result.append(s)

    return result


# UPDATE
@app.put("/students/{student_id}")
def update_student(student_id: int, updated: dict):
    data = read_data()

    for s in data:
        if s["id"] == student_id:
            s["name"] = updated.get("name", s["name"])
            s["age"] = updated.get("age", s["age"])
            write_data(data)
            return s

    raise HTTPException(status_code=404, detail="Student not found")


# SOFT DELETE
@app.delete("/students/{student_id}")
def soft_delete(student_id: int):
    data = read_data()

    for s in data:
        if s["id"] == student_id:
            s["deleted"] = True
            write_data(data)
            return {"message": "Soft deleted"}

    raise HTTPException(status_code=404, detail="Student not found")


# RESTORE
@app.patch("/students/{student_id}/restore")
def restore_student(student_id: int):
    data = read_data()

    for s in data:
        if s["id"] == student_id:
            s["deleted"] = False
            write_data(data)
            return {"message": "Restored"}

    raise HTTPException(status_code=404, detail="Student not found")


# PURGE (permanent delete)
@app.delete("/students/{student_id}/purge")
def purge_student(student_id: int):
    data = read_data()
    new_data = [s for s in data if s["id"] != student_id]

    if len(new_data) == len(data):
        raise HTTPException(status_code=404, detail="Student not found")

    write_data(new_data)
    return {"message": "Permanently deleted"}