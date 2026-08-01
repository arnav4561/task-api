from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Task API")

# In-memory storage
tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Walk the dog", "done": False},
    {"id": 3, "title": "Read a book", "done": True},
]
next_id = 4


class Task(BaseModel):
    title: str
    done: bool = False


@app.get("/")
def root():
    return {"message": "Task API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/tasks", status_code=201)
def create_task(task: Task):
    global next_id
    new_task = {"id": next_id, "title": task.title, "done": task.done}
    tasks.append(new_task)
    next_id += 1
    return new_task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    for t in tasks:
        if t["id"] == task_id:
            t["title"] = task.title
            t["done"] = task.done
            return t
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail="Task not found")