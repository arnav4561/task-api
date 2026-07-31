from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Go to the gym", "done": True},
    {"id": 3, "title": "Read a book", "done": False},
]
next_id = 4
class TaskCreate(BaseModel):
    title: str

@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.post("/tasks", status_code=201)
def create_task(new_task: TaskCreate):
    global next_id
    title = new_task.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title must not be empty")
    task = {"id": next_id, "title": title, "done": False}
    tasks.append(task)
    next_id += 1
    return task