from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from database import SessionLocal
from models import Post

router = APIRouter(prefix="/posts", tags=["posts"])


class PostCreate(BaseModel):
    title: str
    body: Optional[str] = None
    user_id: int


class PostUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    is_published: Optional[bool] = None


def to_dict(p: Post):
    return {
        "id": p.id,
        "title": p.title,
        "body": p.body,
        "user_id": p.user_id,
        "is_published": p.is_published,
    }


@router.post("/", status_code=201)
def create_post(payload: PostCreate):
    with SessionLocal() as db:
        p = Post(title=payload.title, body=payload.body, user_id=payload.user_id)
        db.add(p)
        db.commit()
        db.refresh(p)
        return to_dict(p)


@router.get("/", response_model=List[dict])
def list_posts():
    with SessionLocal() as db:
        posts = db.query(Post).all()
        return [to_dict(p) for p in posts]


@router.get("/{post_id}")
def get_post(post_id: int):
    with SessionLocal() as db:
        p = db.get(Post, post_id)
        if not p:
            raise HTTPException(status_code=404, detail="Post not found")
        return to_dict(p)


@router.put("/{post_id}")
def update_post(post_id: int, payload: PostUpdate):
    with SessionLocal() as db:
        p = db.get(Post, post_id)
        if not p:
            raise HTTPException(status_code=404, detail="Post not found")
        if payload.title is not None:
            p.title = payload.title
        if payload.body is not None:
            p.body = payload.body
        if payload.is_published is not None:
            p.is_published = payload.is_published
        db.add(p)
        db.commit()
        db.refresh(p)
        return to_dict(p)


@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int):
    with SessionLocal() as db:
        p = db.get(Post, post_id)
        if not p:
            raise HTTPException(status_code=404, detail="Post not found")
        db.delete(p)
        db.commit()
        return None
