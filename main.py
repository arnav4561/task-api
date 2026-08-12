from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from repository import TaskRepository

app = FastAPI()

repo = TaskRepository()

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
    return repo.get_all()


@app.get("/tasks/{task_id}", summary="Get a specific task by id")
def get_task(task_id: int):
    task = repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task

@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(new_task: TaskCreate):
    title = new_task.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title must not be empty")
    return repo.create(title)

@app.put("/tasks/{task_id}", summary="Update a task's title/done status")
def update_task(task_id: int, updated: TaskUpdate):
    title = updated.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title must not be empty")
    task = repo.update(task_id, title, updated.done)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a specific task")
def delete_task(task_id: int):
    deleted = repo.delete(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")