# Task API

A small in-memory CRUD API for managing a to-do list, built with FastAPI.
Data is stored only in memory (a Python list) — there is no database yet,
so restarting the server resets the task list back to the 3 seed tasks.

## How to run it

Requires Python 3.10+.

```powershell
python -m venv venv
venv\Scripts\activate
pip install fastapi "uvicorn[standard]"
uvicorn main:app --reload --port 8000
```

Then open:
- `http://localhost:8000/` — API info
- `http://localhost:8000/docs` — Swagger UI (interactive docs)

## Endpoints

| Method | Path            | Meaning                          | Success | Errors                     |
|--------|-----------------|-----------------------------------|---------|------------------------------|
| GET    | `/`             | API info                          | 200     | —                            |
| GET    | `/health`       | Health check                      | 200     | —                            |
| GET    | `/tasks`        | List all tasks                    | 200     | —                            |
| GET    | `/tasks/{id}`   | Get one task                      | 200     | 404 unknown id               |
| POST   | `/tasks`        | Create a task (`{"title": "..."}`)| 201     | 400 missing/empty title      |
| PUT    | `/tasks/{id}`   | Replace a task's title/done       | 200     | 400 bad body · 404 unknown id|
| DELETE | `/tasks/{id}`   | Remove a task                     | 204     | 404 unknown id               |

## Example: create a task

$ curl.exe -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{"title": "Buy milk"}"
HTTP/1.1 201 Created
content-type: application/json

{"id":5,"title":"Buy milk","done":false}

Posting an empty title returns `400` instead of creating a task.
`GET /tasks/99` (an id that doesn't exist) returns `404` with a JSON error.

## A note on Windows/PowerShell

Some `curl.exe` calls with a JSON body (`-d`) failed on this machine due to
PowerShell mangling the quote-escaping — a known PowerShell quirk, not a bug
in the API. Those requests were tested instead with PowerShell's native
`Invoke-WebRequest`, e.g.:

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/tasks/1" -Method Put -ContentType "application/json" -Body '{"title":"Buy oat milk","done":true}' -UseBasicParsing
```

## Swagger UI

`/docs` is generated automatically by FastAPI from the code. Every endpoint
above is listed there with a "Try it out" button that sends real requests.

![Swagger UI screenshot](swagger-screenshot.png)

## The mortality experiment

Create a task, then restart the server (stop it with Ctrl+C, run
`uvicorn main:app --reload --port 8000` again), then `GET /tasks`. The list
goes back to just the 3 seed tasks — everything created while the server was
running is gone, because the data only ever lived in a Python list in
memory, not on disk. Restarting the process wipes the variable along with
it. This is exactly why a real database matters — it's the thing that
survives a restart.

## AI vs me

### My prompt
> make an api, read, create, update, delete as options, use python, framework
> fast api, swagger docs, status codes- 200, 404 not found, 204 no content,
> 201 created, storage in-memory, endpoints: root, health, tasks and then
> get, create, update, delete, tasks should have, id, title, done categories

### What did the AI do better?
Not much, functionally — the CRUD logic itself came out nearly identical to
mine (same loop-and-check pattern for find/update/delete, same in-memory
list). The one place it was arguably cleaner: it used a single `Task`
Pydantic model for both create and update, instead of my two separate
`TaskCreate`/`TaskUpdate` models. That's less code, though I'd argue mine is
slightly more correct — a `POST` body shouldn't really need a `done` field
(a task can't be born already finished), which my split models prevent and
the AI's single model doesn't.

### What did it get wrong or quietly ignore from my prompt?
The AI version **accepts an empty title and creates the task anyway**,
returning `201` with `{"title": ""}` in the response. My own version
explicitly checks for this and returns `400`. My prompt never actually
asked for input validation — I listed status codes but never said "reject
bad input" — so this isn't the AI being wrong exactly, it's the AI building
literally what I asked for and nothing more. But it's a real bug either
way: a production task list with silent empty-title entries is bad
behavior, and the AI didn't push back or flag the gap — it just built it.

### What did my prompt forget to specify — and what did the AI silently decide for you?
- **Validation rules** — the big one. I never mentioned rejecting empty or
  missing titles, so none exists in the AI's version.
- **Error message wording** — the AI used `"Task not found"` for every 404;
  mine says `"Task {id} not found"`, which is more useful for debugging.
- **Response shape for `/` and `/health`** — I said "root" and "health" as
  endpoints but never specified their JSON shape, so the AI picked its own
  (`{"message": "Task API is running"}` vs my `{"name": "Task API",
  "version": "1.0", "endpoints": [...]}`).
- **Whether `done` should be settable on create** — I never said a new task
  starts as not-done; the AI made `done` an optional field on the same
  model used for POST, so a client could technically create a task that's
  already marked done.

### One rematch
Updated prompt: same as above, plus — *"POST and PUT must return 400 if
title is missing or empty (after trimming whitespace); a new task must
always start with done=false, so use separate models for create vs
update."*
What changed: the regenerated version added an explicit `if not title.strip(): raise HTTPException(400, ...)` check in both `create_task` and
`update_task`, and split into two models exactly as instructed — bringing
it in line with my Stage 3/4 behavior. The lesson: the AI's output was
never actually wrong given what it was told — every gap traces back to
something I left unspecified in the prompt.