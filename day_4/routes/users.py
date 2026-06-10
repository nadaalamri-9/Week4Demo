from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from database import SessionLocal
from models import User

router = APIRouter(prefix="/users", tags=["users"])


class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = "user"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


def to_dict(u: User):
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "role": u.role,
        "is_active": u.is_active,
    }


@router.post("/", status_code=201)
def create_user(payload: UserCreate):
    with SessionLocal() as db:
        u = User(email=payload.email, full_name=payload.full_name, role=payload.role)
        db.add(u)
        db.commit()
        db.refresh(u)
        return to_dict(u)


@router.get("/", response_model=List[dict])
def list_users():
    with SessionLocal() as db:
        users = db.query(User).all()
        return [to_dict(u) for u in users]


@router.get("/{user_id}")
def get_user(user_id: int):
    with SessionLocal() as db:
        u = db.get(User, user_id)
        if not u:
            raise HTTPException(status_code=404, detail="User not found")
        return to_dict(u)


@router.put("/{user_id}")
def update_user(user_id: int, payload: UserUpdate):
    with SessionLocal() as db:
        u = db.get(User, user_id)
        if not u:
            raise HTTPException(status_code=404, detail="User not found")
        if payload.full_name is not None:
            u.full_name = payload.full_name
        if payload.role is not None:
            u.role = payload.role
        if payload.is_active is not None:
            u.is_active = payload.is_active
        db.add(u)
        db.commit()
        db.refresh(u)
        return to_dict(u)


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int):
    with SessionLocal() as db:
        u = db.get(User, user_id)
        if not u:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(u)
        db.commit()
        return None
