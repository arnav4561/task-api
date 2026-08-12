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

## Database (SQLite)

### Why SQLite
This project uses SQLite instead of a larger database like PostgreSQL because
it needs no separate server process — the whole database lives in a single
file, and Python's built-in `sqlite3` module talks to it directly, no extra
installs required. For a small project like this, that's the right amount
of infrastructure: enough to get real persistence, without the overhead of
running and configuring a separate database server.

### Where the database lives
The database is a single file, `tasks.db`, created automatically in the
project root the first time the app runs. It's excluded from git via
`.gitignore` — it's runtime data, not source code, so a fresh clone of this
repo won't include it. Instead, `database.py`'s `init_db()` function creates
the file and the `tasks` table (and seeds 3 example tasks) automatically on
first startup, so a stranger cloning this repo gets a working database with
zero manual setup.

### How to run it
Same as Assignment 1 — no new dependencies, since `sqlite3` ships with
Python.

```powershell
python -m venv venv
venv\Scripts\activate
pip install fastapi "uvicorn[standard]"
uvicorn main:app --reload --port 8000
```

`tasks.db` will appear automatically on first run.

### Viewing the database directly
[DB Browser for SQLite](https://sqlitebrowser.org/) was used to inspect and
manually query the database outside the API.

![DB Browser screenshot](db-browser-screenshot.png)

### Example SQL query
```sql
SELECT * FROM tasks WHERE done = 1;
```
Running this in DB Browser's Execute SQL tab, then hitting `GET /tasks` in
the running API immediately afterward, shows the exact same data —
confirming the API and the database viewer are just two different windows
onto the same file. Marking a task done directly through SQL, with zero
code changes, was reflected instantly through the API.

### What changed vs. Assignment 1
The API itself — every endpoint, path, request/response shape, and status
code — is unchanged. The only difference is what happens *inside* each
endpoint: instead of reading/writing a Python list that lived in memory,
each endpoint now runs a SQL query against `tasks.db`. The practical result:
data now survives a server restart, which it never did before.

One visible side effect worth noting: SQLite stores booleans as integers,
so `done` now comes back as `0`/`1` in the JSON response instead of
`true`/`false` as it did in Assignment 1.

## Containerized stack (Postgres + Docker Compose)

### Overview
The app now runs alongside a real Postgres database, both inside Docker,
started together with a single command:

```powershell
docker compose up
```

This replaces the earlier setup (a local SQLite file, or a manually-run
Postgres container) with a fully reproducible stack — anyone cloning this
repo can run one command and get a working app + database, with no manual
setup beyond creating a `.env` file.

### Postgres in Docker, with a volume
Postgres runs as the `db` service in `docker-compose.yml`, using the
official `postgres:16` image. Data is stored in a named Docker volume,
`pgdata`, mapped to `/var/lib/postgresql/data` inside the container — this
is what allows the database to survive containers being stopped, removed,
and recreated (`docker compose down` followed by `docker compose up`).

The `tasks` table is created automatically on first startup via `init.sql`,
mounted into Postgres's `/docker-entrypoint-initdb.d/` directory — Postgres
runs any SQL file placed there the first time it starts with an empty
database.

### Connection string via `.env`
The database connection string lives in `.env`:

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/taskdb

`.env` is gitignored — it's never committed. A `.env.example` with the same
shape is committed instead, so anyone cloning the repo knows what variable
to set. Inside Docker Compose specifically, the `app` service overrides this
with `db` as the hostname instead of `localhost`, since containers reach
each other by service name, not `localhost`, once both are running inside
Compose's network.

### Repository swap — service and routes unchanged
This is the architectural point of the whole assignment, and it's true here:
`main.py`'s route functions (`get_tasks`, `get_task`, `create_task`,
`update_task`, `delete_task`) are functionally identical to the SQLite
version from the previous assignment. Each one still does the same three
things: validate input if needed, call the storage layer, translate the
result into an HTTP response. The only thing that changed is what's inside
`repository.py` — SQLite's `sqlite3` + `?` placeholders were replaced with
`psycopg2` + `%s` placeholders, talking to Postgres instead. No route
signature, path, or status code changed.

### Proving persistence
To prove data survives a full stack restart (not just a database restart,
but the app container too):

1. Created a task via `POST /tasks` — confirmed with `GET /tasks`.
2. Ran `docker compose down` — this stops **and removes** both containers
   entirely (a real teardown, not a pause).
3. Ran `docker compose up` again — fresh containers were created from
   scratch.
4. Ran `GET /tasks` again — the task created in step 1 was still there.

The Postgres startup log confirmed this directly, logging
`PostgreSQL Database directory appears to contain a database; Skipping
initialization` — meaning it found existing data in the `pgdata` volume
rather than starting from empty, even though the containers themselves
had been completely removed and recreated.

### How to run it
```powershell
# 1. copy the example env file and adjust if needed
cp .env.example .env

# 2. start the whole stack
docker compose up
```
The app will be available at `http://localhost:8000`, Postgres at
`localhost:5432`.