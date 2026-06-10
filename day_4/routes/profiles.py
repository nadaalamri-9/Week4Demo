from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from database import SessionLocal
from models import UserProfile

router = APIRouter(prefix="/profiles", tags=["profiles"])


class ProfileCreate(BaseModel):
    user_id: int
    bio: Optional[str] = None
    website: Optional[str] = None


class ProfileUpdate(BaseModel):
    bio: Optional[str] = None
    website: Optional[str] = None


def to_dict(p: UserProfile):
    return {
        "id": p.id,
        "user_id": p.user_id,
        "bio": p.bio,
        "website": p.website,
    }


@router.post("/", status_code=201)
def create_profile(payload: ProfileCreate):
    with SessionLocal() as db:
        prof = UserProfile(user_id=payload.user_id, bio=payload.bio, website=payload.website)
        db.add(prof)
        db.commit()
        db.refresh(prof)
        return to_dict(prof)


@router.get("/", response_model=List[dict])
def list_profiles():
    with SessionLocal() as db:
        items = db.query(UserProfile).all()
        return [to_dict(p) for p in items]


@router.get("/{profile_id}")
def get_profile(profile_id: int):
    with SessionLocal() as db:
        p = db.get(UserProfile, profile_id)
        if not p:
            raise HTTPException(status_code=404, detail="Profile not found")
        return to_dict(p)


@router.put("/{profile_id}")
def update_profile(profile_id: int, payload: ProfileUpdate):
    with SessionLocal() as db:
        p = db.get(UserProfile, profile_id)
        if not p:
            raise HTTPException(status_code=404, detail="Profile not found")
        if payload.bio is not None:
            p.bio = payload.bio
        if payload.website is not None:
            p.website = payload.website
        db.add(p)
        db.commit()
        db.refresh(p)
        return to_dict(p)


@router.delete("/{profile_id}", status_code=204)
def delete_profile(profile_id: int):
    with SessionLocal() as db:
        p = db.get(UserProfile, profile_id)
        if not p:
            raise HTTPException(status_code=404, detail="Profile not found")
        db.delete(p)
        db.commit()
        return None
