"""
LAB 6 - Bulletproof the API: Validation, Errors, and Test Databases
====================================================================
Do this AFTER lesson_06_errors_and_testing.py.

THE SCENARIO: a signup API that currently trusts everyone and
crashes on duplicates. You will harden it in three steps:

  * Task 1: validate input with Pydantic  (bad email / short password -> 422)
  * Task 2: handle IntegrityError         (duplicate email -> 409, not a crash)
  * Task 3: dependency override           (tests write to a TEST database)

HOW TO WORK:
  This is the FINAL lab - no steps, no patterns, no hints. Each
  task states only the GOAL: how your API must behave when you are
  done. How you get there is entirely up to you. Everything you
  need was covered in lesson 6.

  1. Write your code where it says "WRITE YOUR CODE HERE"
     (Tasks 1 and 2 EDIT code that already exists - the markers
      show you which lines to change).
  2. Run the file:   python lab_06_errors_testing.py
  3. The checker prints PASS or FAIL for each task.
  4. Fix, re-run, repeat. Both databases are rebuilt every run.

RULES:
  * Don't edit anything below "THE CHECKER" line.
  * Don't open lab_06_errors_testing_solution.py until all 3 pass.
"""

import os
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ---------------------------------------------------------------
# Provided setup - no changes needed in this block
# ---------------------------------------------------------------

for f in ("lab_errors.db", "lab_errors_test.db"):
    if os.path.exists(f):
        os.remove(f)

engine = create_engine("sqlite:///./lab_errors.db",
                       connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    model_config = {"from_attributes": True}


app = FastAPI(title="Lab 6 - Hardened Signup API")


# ===============================================================
# TASK 1 - Validate input with Pydantic
# ===============================================================
# GOAL when finished:
#   an invalid email address          -> rejected with HTTP 422
#   a password shorter than 8 chars   -> rejected with HTTP 422
#   ...both BEFORE your route code even runs.
#
# Edit the schema below.
# ---------------------------------------------------------------

class UserCreate(BaseModel):
    # ---- EDIT THESE LINES (Task 1) ----
    email: EmailStr
    full_name: str
    password: str = Field(min_length=8)
    # -----------------------------------


# ===============================================================
# TASK 2 - Turn a crash into a clean 409
# ===============================================================
# GOAL when finished:
#   Registering the same email twice returns HTTP 409 with the
#   exact detail text "Email already registered" - instead of
#   crashing. And after a failed signup, the API must keep working
#   normally for the next request.
#
# RIGHT NOW: the route below is naive. A duplicate email makes it
# explode in the user's face. Run the file and watch Task 2 FAIL
# with that exact crash - then fix it.
#
# Edit the route body below.
# ---------------------------------------------------------------

@app.post("/users", response_model=UserOut, status_code=201)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = User(email=user_in.email, full_name=user_in.full_name)
    # ---- EDIT THESE LINES (Task 2) ----   
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")
    db.refresh(user)
    return user
    # -----------------------------------


# ===============================================================
# TASK 3 - Point the tests at a TEST database
# ===============================================================
# GOAL when finished:
#   Every request made by the checker writes to lab_errors_test.db,
#   and the development database (lab_errors.db) stays EMPTY.
#
# The test engine and TestSession are provided below. Make the app
# use them whenever a route asks for a database session - WITHOUT
# touching get_db or the routes themselves.
# ---------------------------------------------------------------

# Provided: a second engine pointing at the TEST database file.
test_engine = create_engine("sqlite:///./lab_errors_test.db",
                            connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False,
bind=test_engine)
Base.metadata.create_all(bind=test_engine)

# ---- WRITE YOUR CODE HERE (Task 3) ----

def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

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
    resp = client.post("/users", json={
        "email": "not-an-email", "full_name": "X",
        "password": "longenough123"})
    assert resp.status_code == 422, \
        f"an invalid email got {resp.status_code}, expected 422"
    resp = client.post("/users", json={
        "email": "shorty@mail.com", "full_name": "X", "password": "abc"})
    assert resp.status_code == 422, \
        f"a 3-letter password got {resp.status_code}, expected 422"


def check_task_2():
    payload = {"email": "dup@mail.com", "full_name": "Dup",
               "password": "longenough123"}
    resp = client.post("/users", json=payload)
    assert resp.status_code == 201, f"first signup failed: {resp.status_code}"
    try:
        resp = client.post("/users", json=payload)  # the duplicate!
    except Exception as error:
        raise AssertionError(
            "the route CRASHED on a duplicate email instead of "
            "returning 409") from error
    assert resp.status_code == 409, \
        f"a duplicate email got {resp.status_code}, expected 409"
    assert resp.json()["detail"] == "Email already registered", \
        f"expected detail 'Email already registered', got {resp.json()}"


def check_task_3():
    payload = {"email": "isolated@mail.com", "full_name": "Iso",
               "password": "longenough123"}
    resp = client.post("/users", json=payload)
    assert resp.status_code == 201, f"signup failed: {resp.status_code}"
    # The DEV database must NOT contain this user...
    dev = SessionLocal()
    in_dev = (dev.query(User)
              .filter(User.email == "isolated@mail.com").first())
    dev.close()
    assert in_dev is None, \
        "the user landed in the DEV database"
    # ...but the TEST database must:
    test = TestSession()
    in_test = (test.query(User)
               .filter(User.email == "isolated@mail.com").first())
    test.close()
    assert in_test is not None, \
        "the user is not in the test database"


print("\n--- Checking your lab ---")
check("Task 1: bad input is rejected with 422", check_task_1)
check("Task 2: duplicate email answers 409", check_task_2)
check("Task 3: requests write to the test database", check_task_3)

if all(results):
    print("\nALL TASKS PASS - validated, error-handled, and testable!")
else:
    print(f"\n{results.count(True)}/3 tasks passing. "
          "Fix the first FAIL and run again.")
