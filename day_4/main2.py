from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database2 import engine, Base, get_db
from models2 import Todo
from schemas2 import TodoCreate, TodoOut

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todos API")


@app.post("/todos", response_model=TodoOut, status_code=201)
def create_todo(todo_in: TodoCreate, db: Session = Depends(get_db)):
    todo = Todo(title=todo_in.title)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@app.get("/todos", response_model=list[TodoOut])
def list_todos(db: Session = Depends(get_db)):
    return db.query(Todo).all()


@app.get("/todos/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo