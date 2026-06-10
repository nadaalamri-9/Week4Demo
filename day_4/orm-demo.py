from database import SessionLocal, engine, Base
from models import User, Post, UserProfile


def run_demo():
    # create schema
    Base.metadata.create_all(bind=engine)
    print("Created tables (if not exist): users, posts")

    with SessionLocal() as db:
        # 1) create a user
        alice = User(email="alice@example.com", full_name="Alice Example", role="admin")
        db.add(alice)
        db.commit()
        db.refresh(alice)
        print("Inserted User; database set id:", alice.id)

        # 2) create two posts for alice
        p1 = Post(title="First post", body="Hello world", user_id=alice.id)
        p2 = Post(title="Second post", body="ORMs are neat", user_id=alice.id)
        db.add_all([p1, p2])
        db.commit()

        # 2.5) create a one-to-one profile for alice
        prof = UserProfile(user_id=alice.id, bio="Instructor of ORMs", website="https://example.com/alice")
        db.add(prof)
        db.commit()
        db.refresh(prof)
        print("Inserted UserProfile; database set id:", prof.id)

        # 3) query all users and print
        users = db.query(User).all()
        print("\nUsers from db.query(User).all():")
        for u in users:
            print(u)

        # Structured serializer to show relations clearly for teaching
        def serialize_user(u: User):
            return {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
                "is_active": u.is_active,
                "posts": [
                    {"id": p.id, "title": p.title, "user_id": p.user_id}
                    for p in u.posts
                ],
                "profile": (
                    {"id": u.profile.id, "bio": u.profile.bio, "website": u.profile.website}
                    if u.profile else None
                ),
            }

        print("\nStructured user with relations:")
        print(serialize_user(alice_from_db))

        # 4) access relationship without writing SQL
        print("\nAccessing alice.posts (no explicit JOIN in your code):")
        alice_from_db = db.query(User).filter(User.email == "alice@example.com").first()
        print("User:", alice_from_db)
        print("Posts attached to this user:")
        for post in alice_from_db.posts:
            print(post)

        # show one-to-one relationship access
        print("\nAccessing alice.profile (one-to-one):")
        print(alice_from_db.profile)
        print("profile.user ->", alice_from_db.profile.user)

        # 5) show generated SQL for a query
        q = db.query(User).filter(User.is_active == True)
        print("\nGenerated SQL for db.query(User).filter(User.is_active == True):")
        print(str(q))


if __name__ == "__main__":
    run_demo()
