"""
All the security plumbing: password hashing, JWT creation/verification,
and the FastAPI dependencies that protect routes. The files in routes/
import from here -- this module defines HOW auth works, the routers
decide WHERE it gets applied.

The flow looks like this:

register -> we hash the password and store the user
login    -> we verify the password and hand back a signed JWT
any protected route -> client sends "Authorization: Bearer <token>",
get_current_user decodes it and loads the user
admin route -> require_admin runs get_current_user first, then also
checks the role column

LAB: this file has TODO(1) through TODO(5). Fill them in following
along in class. Until a TODO is done, the matching endpoints return a
500 -- that's expected, it's the NotImplementedError bubbling up.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User

# In production this comes from an environment variable, never source
# code -- anyone who has this key can forge tokens for any user.
SECRET_KEY = "change-me-in-production-this-is-a-classroom-demo"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# HTTPBearer pulls the token out of the "Authorization: Bearer xxx"
# header for us and returns 403 if the header is missing.
bearer_scheme = HTTPBearer()


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """
    bcrypt is a one-way hash designed for passwords: it's deliberately
    slow (to make brute-forcing expensive) and salts automatically (so
    two users with the same password get different hashes).
    """
    # TODO(1): hash the password with bcrypt and return the hash as a
    # string. You'll need bcrypt.hashpw(), which takes the password as
    # bytes plus a salt from bcrypt.gensalt(), and returns bytes.
    # (.encode() turns str into bytes, .decode() turns bytes back.)

    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    raise NotImplementedError("TODO(1)")


def verify_password(plain: str, hashed: str) -> bool:
    """
    You can't "decrypt" a bcrypt hash. Instead, the check hashes the
    attempt with the same salt and compares the results.
    """
    # TODO(2): return True if `plain` matches `hashed`, using
    # bcrypt.checkpw(). Same bytes/str dance as TODO(1).

    return bcrypt.checkpw(plain.encode(), hashed.encode())

    raise NotImplementedError("TODO(2)")


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

def create_access_token(user: User) -> str:
    """
    A JWT is three base64 chunks: header.payload.signature. The payload
    (our "claims") is readable by anyone -- paste a token into jwt.io
    and look -- so never put secrets in it. What makes it secure is the
    signature: it's computed with SECRET_KEY, so if anyone tampers with
    the payload the signature stops matching and we reject the token.
    """
    # TODO(3): build the payload dict and return the encoded token.
    # The payload needs three claims:
    #   "sub"  -> the user's id, as a string (the spec wants a string)
    #   "role" -> the user's role, so the frontend can show/hide admin UI
    #   "exp"  -> when the token dies: datetime.now(timezone.utc) plus
    #             timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Then sign it with jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM).

    payload = {
        "sub": str(user.id),
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    raise NotImplementedError("TODO(3)")


# ---------------------------------------------------------------------------
# Route dependencies
# ---------------------------------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency for any route that requires a logged-in user. Decodes the
    token, then loads the user from the database. If anything is off --
    bad signature, expired, user deleted since the token was issued --
    the request stops here with a 401.
    """
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        # Part of the HTTP spec for 401s: tells the client what auth
        # scheme the server expects.
        headers={"WWW-Authenticate": "Bearer"},
    )

    # TODO(4): three steps here.
    #   1. Decode the token with jwt.decode(credentials.credentials,
    #      SECRET_KEY, algorithms=[ALGORITHM]) -- it verifies the
    #      signature AND the exp claim in one call. Wrap it in
    #      try/except jwt.PyJWTError and raise `unauthorized` on failure.
    #   2. Load the user: query User, filtering on
    #      User.id == int(payload["sub"]), and take .first().
    #   3. If no user came back, raise `unauthorized`. Otherwise return
    #      the user.

    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])

    except jwt.PyJWTError:
        raise unauthorized

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise unauthorized

    return user

    raise NotImplementedError("TODO(4)")


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    RBAC happens here. This dependency chains on top of get_current_user
    (so the token check already passed), then adds one more rule: the
    role must be "admin". 401 means "we don't know who you are";
    403 means "we know who you are, and you're not allowed".
    """
    # TODO(5): if current_user's role is not "admin", raise an
    # HTTPException with status_code=status.HTTP_403_FORBIDDEN and a
    # short detail message. Otherwise return current_user.

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

    raise NotImplementedError("TODO(5)")
