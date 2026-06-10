from .users import router as users_router
from .posts import router as posts_router
from .profiles import router as profiles_router

__all__ = ["users_router", "posts_router", "profiles_router"]
