from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import Base, engine, get_db
import model

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI Fundamentals API",
    description="A beginner-friendly FastAPI project setup tutorial.",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI Fundamentals"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/blogs")
def add_blog(blog: model.BlogCreate, db: Session = Depends(get_db)):
    new_blog = model.Blogs(
        userid=blog.userid,
        post=blog.post,
        descriptions=blog.descriptions,
    )
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.get("/users/{user_id}/blogs")
def get_user_blogs(user_id: int, db: Session = Depends(get_db)):
    return db.query(model.Blogs).filter(model.Blogs.userid == user_id).all()