from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import init_db, get_connection

init_db()

app = FastAPI()

class TaskCreate(BaseModel):
    title: str
class TaskUpdate(BaseModel):
    title: str
    done: bool = False

@app.get("/", summary="API info")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health", summary="Health check")
def health_check():
    return {"status": "ok"}

@app.get("/tasks", summary="List all tasks")
def get_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/tasks/{task_id}", summary="Get a specific task by id")
def get_task(task_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return dict(row)

@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(new_task: TaskCreate):
    global next_id
    title = new_task.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title must not be empty")
    task = {"id": next_id, "title": title, "done": False}
    tasks.append(task)
    next_id += 1
    return task

@app.put("/tasks/{task_id}", summary="Update a task's title/done status")
def update_task(task_id: int, updated: TaskUpdate):
    title = updated.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title must not be empty")
    for task in tasks:
        if task["id"] == task_id:
            task["title"] = title
            task["done"] = updated.done
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a specific task")
def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")