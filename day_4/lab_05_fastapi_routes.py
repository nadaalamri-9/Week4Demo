"""
LAB 5 - Build Database Routes with FastAPI
===========================================
Do this AFTER lesson_05_fastapi_integration.py.

THE SCENARIO: a todo-list API. The model and the Pydantic schemas
are provided - YOUR job is the plumbing between FastAPI and the
database: the session dependency and three routes.

  * Task 1: write get_db() with yield
  * Task 2: POST /todos   (add -> commit -> refresh -> return)
  * Task 3: GET /todos    (return every todo)
  * Task 4: GET /todos/{todo_id}   (one todo, or a clean 404)

HOW TO WORK:
  1. Read the task instructions and the SYNTAX TEMPLATE above it.
     The templates use the users API from the lesson - adapt them.
  2. Write your code where it says "WRITE YOUR CODE HERE".
  3. Run the file:   python lab_05_fastapi_routes.py
  4. The checker calls your API with a test client and prints
     PASS or FAIL for each task, with a hint.
  5. Fix, re-run, repeat. The database is rebuilt every run.

BONUS once everything passes: run it as a real server and click
around in Swagger UI:
    uvicorn lab_05_fastapi_routes:app --reload
    -> http://127.0.0.1:8000/docs

RULES:
  * Don't edit anything below "THE CHECKER" line.
  * Don't open lab_05_fastapi_routes_solution.py until all 4 pass.
"""

import os

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ---------------------------------------------------------------
# Provided setup - no changes needed in this block
# ---------------------------------------------------------------

if os.path.exists("lab_fastapi.db"):
    os.remove("lab_fastapi.db")

engine = create_engine("sqlite:///./lab_fastapi.db",
                       connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    done = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)


class TodoCreate(BaseModel):
    """What the client sends to create a todo."""
    title: str


class TodoOut(BaseModel):
    """What we send back."""
    id: int
    title: str
    done: bool
    model_config = {"from_attributes": True}


app = FastAPI(title="Lab 5 - Todos API")


# ===============================================================
# TASK 1 - The get_db() dependency
# ===============================================================
# GOAL when finished:
#   get_db() opens ONE session, hands it to the route with yield,
#   and ALWAYS closes it afterward - even if the route crashed.
#
# STEPS:
#   1a. Create a session:  db = SessionLocal()
#   1b. yield it inside a try block
#       (yield, not return! return would close the door before
#        the route even runs)
#   1c. Close it in a finally block:  db.close()
#
# --------------- SYNTAX TEMPLATE (from the lesson) -------------
#
#   def get_db():
#       db = SessionLocal()
#       try:
#           yield db
#       finally:
#           db.close()
#
# (Yes, the template IS the answer for this one - get_db is a
#  recipe you should be able to write from memory. Type it out!)
# ---------------------------------------------------------------

def get_db():
    # ---- WRITE YOUR CODE HERE (about 5 lines) ----
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    pass


# ===============================================================
# TASK 2 - POST /todos
# ===============================================================
# GOAL when finished:
#   POST /todos with {"title": "Buy milk"} returns 201 and the
#   saved todo - WITH the id the database assigned.
#
# STEPS:
#   2a. Decorate with:
#         @app.post("/todos", response_model=TodoOut, status_code=201)
#   2b. The function takes (todo_in: TodoCreate,
#                           db: Session = Depends(get_db))
#   2c. Build the row:      todo = Todo(title=todo_in.title)
#   2d. The famous trio:    db.add(todo) -> db.commit() -> db.refresh(todo)
#       (refresh reloads the object so todo.id is filled in!)
#   2e. return todo
#
# --------------- SYNTAX TEMPLATE (from the lesson) -------------
#
#   @app.post("/users", response_model=UserOut, status_code=201)
#   def create_user(user_in: UserCreate,
#                   db: Session = Depends(get_db)):
#       user = User(email=user_in.email)
#       db.add(user)
#       db.commit()
#       db.refresh(user)
#       return user
# ---------------------------------------------------------------

# ---- WRITE YOUR CODE HERE (Task 2: about 7 lines) ----

@app.post("/todos", response_model=TodoOut, status_code=201)
def create_todo(todo_in: TodoCreate, db: Session = Depends(get_db)):
    todo = Todo(title=todo_in.title)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


# ===============================================================
# TASK 3 - GET /todos
# ===============================================================
# GOAL when finished:
#   GET /todos returns a JSON list of every todo.
#
# STEPS:
#   3a. Decorate with:
#         @app.get("/todos", response_model=list[TodoOut])
#   3b. Take db: Session = Depends(get_db)
#   3c. return db.query(Todo).all()
#
# --------------- SYNTAX TEMPLATE (from the lesson) -------------
#
#   @app.get("/users", response_model=list[UserOut])
#   def list_users(db: Session = Depends(get_db)):
#       return db.query(User).all()
# ---------------------------------------------------------------

# ---- WRITE YOUR CODE HERE (Task 3: about 3 lines) ----

@app.get("/todos", response_model=list[TodoOut])
def list_todos(db: Session = Depends(get_db)):
    return db.query(Todo).all()


# ===============================================================
# TASK 4 - GET /todos/{todo_id}
# ===============================================================
# GOAL when finished:
#   GET /todos/1   -> 200 and the todo
#   GET /todos/999 -> 404 with detail "Todo not found"
#
# STEPS:
#   4a. Decorate with:
#         @app.get("/todos/{todo_id}", response_model=TodoOut)
#   4b. The function takes (todo_id: int,
#                           db: Session = Depends(get_db))
#   4c. Look it up by primary key:  todo = db.get(Todo, todo_id)
#   4d. db.get returns None when not found - turn that into:
#         raise HTTPException(status_code=404, detail="Todo not found")
#   4e. return todo
#
# --------------- SYNTAX TEMPLATE (from the lesson) -------------
#
#   @app.get("/users/{user_id}", response_model=UserOut)
#   def get_user(user_id: int, db: Session = Depends(get_db)):
#       user = db.get(User, user_id)
#       if user is None:
#           raise HTTPException(status_code=404,
#                               detail="User not found")
#       return user
# ---------------------------------------------------------------

# ---- WRITE YOUR CODE HERE (Task 4: about 6 lines) ----

@app.get("/todos/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


# ===============================================================
# THE CHECKER - do not edit below this line
# ===============================================================

from fastapi.testclient import TestClient

client = TestClient(app)
results = []


def check(task_name, test_function):
    """Run one check and report PASS or FAIL with the reason."""
    try:
        test_function()
        results.append(True)
        print(f"PASS  {task_name}")
    except Exception as error:
        results.append(False)
        print(f"FAIL  {task_name}")
        print(f"      -> {type(error).__name__}: {error}")


def check_task_1():
    gen = get_db()
    assert gen is not None, "get_db returned None - is it still `pass`?"
    assert hasattr(gen, "__next__"), \
        "get_db must use yield, making it a generator"
    db = next(gen)
    assert db is not None, "get_db yielded None instead of a session"
    assert hasattr(db, "query"), "get_db did not yield a Session"
    gen.close()  # triggers your finally block


def check_task_2():
    resp = client.post("/todos", json={"title": "Buy milk"})
    assert resp.status_code != 404, \
        "POST /todos does not exist - did you write the route?"
    assert resp.status_code == 201, \
        (f"expected 201, got {resp.status_code} - set "
         "status_code=201 in the decorator")
    body = resp.json()
    assert body["title"] == "Buy milk"
    assert body.get("id") is not None, \
        "the returned todo has no id - did you db.refresh(todo)?"


def check_task_3():
    client.post("/todos", json={"title": "Walk the dog"})
    resp = client.get("/todos")
    assert resp.status_code != 404, \
        "GET /todos does not exist - did you write the route?"
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.json()]
    assert "Buy milk" in titles and "Walk the dog" in titles, \
        f"expected both todos in the list, got {titles}"


def check_task_4():
    resp = client.get("/todos/1")
    assert resp.status_code != 405, \
        "GET /todos/1 hit the wrong route - is the path /todos/{todo_id}?"
    assert resp.status_code == 200, \
        f"GET /todos/1 should be 200, got {resp.status_code}"
    assert resp.json()["id"] == 1
    resp = client.get("/todos/999")
    assert resp.status_code == 404, \
        (f"GET /todos/999 should be 404, got {resp.status_code} - "
         "raise HTTPException when db.get returns None")


print("\n--- Checking your lab ---")
check("Task 1: get_db() with yield", check_task_1)
check("Task 2: POST /todos (add, commit, refresh)", check_task_2)
check("Task 3: GET /todos", check_task_3)
check("Task 4: GET /todos/{id} with 404", check_task_4)

if all(results):
    print("\nALL TASKS PASS - you wired FastAPI to a database!")
    print("Now run it for real:  uvicorn lab_05_fastapi_routes:app --reload")
else:
    print(f"\n{results.count(True)}/4 tasks passing. "
          "Fix the first FAIL and run again.")
