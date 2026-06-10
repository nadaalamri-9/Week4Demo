"""
LAB - Build Every Relationship Type Yourself
=============================================
Do this AFTER lesson_04b_relationships.py.

THE SCENARIO: a small public library.

  * An Author writes many Books                      -> ONE-TO-MANY
  * A Member has exactly one LibraryCard             -> ONE-TO-ONE
  * Members borrow many Books, Books are borrowed
    by many Members, linked through a Loan           -> MANY-TO-MANY

YOUR JOB: the models below have their basic columns, but ALL the
links between them are missing. Complete Tasks 1, 2, and 3 in order.

HOW TO WORK:
  1. Read the task instructions and the SYNTAX TEMPLATE above it.
     The template shows the PATTERN using the blog example from the
     lesson (User/Post) - your job is to adapt it to the library.
  2. Write your code where it says "WRITE YOUR CODE HERE".
  3. Run the file:   python lab_relationships.py
  4. The checker at the bottom prints PASS or FAIL for each task,
     with a hint about what went wrong.
  5. Fix, re-run, repeat. Re-running is always safe - the database
     is rebuilt from scratch every time.

RULES:
  * Don't edit anything below "THE CHECKER" line.
  * Don't open lab_relationships_solution.py until all 3 tasks pass
    (or you have been stuck for a genuinely long time!).
"""

import os
from datetime import datetime

from sqlalchemy import (create_engine, Column, Integer, String, Boolean,
                        DateTime, ForeignKey)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Fresh database every run, so you can re-run as often as you like.
if os.path.exists("lab_relationships.db"):
    os.remove("lab_relationships.db")

engine = create_engine("sqlite:///./lab_relationships.db")
Base = declarative_base()


# ===============================================================
# TASK 1 - ONE-TO-MANY: an Author writes many Books
# ===============================================================
# GOAL when finished:
#   author.books        -> a LIST of that author's Book objects
#   book.author         -> the ONE Author who wrote it
#
# STEPS:
#   1a. On Book:   add a ForeignKey column named  author_id
#   1b. On Author: add a relationship named       books
#   1c. On Book:   add a relationship named       author
#
# REMEMBER: the ForeignKey always goes on the "many" side.
# An Author has many Books, so the Book is the child.
#
# --------------- SYNTAX TEMPLATE (from the lesson) -------------
# This is how the blog did it. Adapt the names to the library:
#
#   class User(Base):                    # the "one" side (parent)
#       posts = relationship("Post", back_populates="author")
#
#   class Post(Base):                    # the "many" side (child)
#       user_id = Column(Integer, ForeignKey("users.id"),
#                        index=True, nullable=False)
#       author = relationship("User", back_populates="posts")
#
# WATCH OUT: ForeignKey takes "tablename.column" (lowercase table
# name, like "users.id") - NOT the class name "User.id".
# ---------------------------------------------------------------


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # Task 1b: add the `books` relationship.
    # It points at "Book" and back_populates the `author` attribute
    # you will create on Book in Task 1c.
    #
    # ---- WRITE YOUR CODE HERE (1 line) ----

    books = relationship("Book", back_populates="author")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)

    # Task 1a: add the `author_id` column.
    # It is an Integer ForeignKey to the authors table's id column.
    # Make it indexed (we filter by author a lot) and required.
    #
    # ---- WRITE YOUR CODE HERE (1 line) ----
    author_id = Column(Integer, ForeignKey("authors.id"), index=True, nullable=False)

    # Task 1c: add the `author` relationship.
    # It points at "Author" and back_populates the `books` attribute
    # from Task 1b. (The two back_populates values point at EACH
    # OTHER: "books" here... wait, which name goes where? Check the
    # template: each side names the attribute ON THE OTHER MODEL.)
    #
    # ---- WRITE YOUR CODE HERE (1 line) ----

    author = relationship("Author", back_populates="books")


# ===============================================================
# TASK 2 - ONE-TO-ONE: a Member has exactly one LibraryCard
# ===============================================================
# GOAL when finished:
#   member.card         -> ONE LibraryCard object (NOT a list!)
#   card.member         -> the Member who owns it
#   ...and the database REFUSES a second card for the same member.
#
# STEPS:
#   2a. On LibraryCard: add a ForeignKey column named  member_id
#   2b. On Member:      add a relationship named       card
#   2c. On LibraryCard: add a relationship named       member
#
# A one-to-one is a one-to-many PLUS two extra settings:
#   * unique=True on the ForeignKey column        (step 2a)
#       -> the DATABASE blocks a second card per member
#   * uselist=False on the parent's relationship  (step 2b)
#       -> PYTHON returns one object instead of a list
#
# --------------- SYNTAX TEMPLATE (from the lesson) -------------
#
#   class User(Base):                    # the parent
#       profile = relationship("UserProfile", back_populates="user",
#                              uselist=False)
#
#   class UserProfile(Base):             # the child
#       user_id = Column(Integer, ForeignKey("users.id"),
#                        unique=True, nullable=False)
#       user = relationship("User", back_populates="profile")
# ---------------------------------------------------------------

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)

    # Task 2b: add the `card` relationship.
    # Points at "LibraryCard", back_populates the `member` attribute
    # from Task 2c, and needs ONE extra argument so member.card is a
    # single object, not a list. (Which argument? See the template.)
    #
    # ---- WRITE YOUR CODE HERE (1 line) ----

    card = relationship("LibraryCard", back_populates="member", uselist=False)

    # Task 3c: come back DURING TASK 3 and add the `loans`
    # relationship. Points at "Loan", back_populates the `member`
    # attribute you will create on Loan in Task 3b.
    #
    # ---- WRITE YOUR CODE HERE (1 line) ----
    
    loans = relationship("Loan", back_populates="member")


class LibraryCard(Base):
    __tablename__ = "library_cards"

    id = Column(Integer, primary_key=True)
    card_number = Column(String, unique=True, nullable=False)

    # Task 2a: add the `member_id` column.
    # Integer ForeignKey to the members table's id column, required,
    # and with the ONE extra constraint that makes this one-to-one
    # at the database level. (Which constraint? See the template.)
    #
    # ---- WRITE YOUR CODE HERE (1 line) ----
    member_id = Column(Integer, ForeignKey("members.id"), unique=True, nullable=False)

    # Task 2c: add the `member` relationship.
    # Points at "Member", back_populates the `card` attribute.
    #
    # ---- WRITE YOUR CODE HERE (1 line) ----
    member = relationship("Member", back_populates="card")

# ===============================================================
# TASK 3 - MANY-TO-MANY: Members borrow Books through a Loan
# ===============================================================
# GOAL when finished:
#   member.loans        -> a LIST of that member's Loan objects
#   loan.member         -> the Member who borrowed
#   loan.book           -> the Book that was borrowed
#
# STEPS:
#   3a. On Loan:   add TWO ForeignKey columns: member_id and book_id
#   3b. On Loan:   add TWO relationships: member and book
#   3c. On Member: go BACK UP and add the `loans` relationship
#
# WHY a Loan table at all? One ForeignKey can only point one way.
# A member borrows many books AND a book is borrowed by many
# members - so we need one ROW PER PAIR, in its own table.
# That junction table also carries data about the pair itself
# (borrowed_at, returned) - already provided for you below.
#
# --------------- SYNTAX TEMPLATE (from the lesson) -------------
#
#   class Enrollment(Base):              # the junction table
#       student_id = Column(Integer, ForeignKey("students.id"),
#                           index=True, nullable=False)
#       course_id = Column(Integer, ForeignKey("courses.id"),
#                          index=True, nullable=False)
#       student = relationship("Student", back_populates="enrollments")
#       course = relationship("Course")  # one-directional is fine
#
#   class Student(Base):
#       enrollments = relationship("Enrollment",
#                                  back_populates="student")
#
# NOTE: in this lab, `book` on Loan does NOT need back_populates -
# we never navigate book.loans. A one-directional relationship()
# with just the model name is enough.
# ---------------------------------------------------------------

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True)

    # Data about the PAIR is provided for you - no changes needed:
    borrowed_at = Column(DateTime, default=datetime.utcnow)
    returned = Column(Boolean, default=False)

    # Task 3a: add the `member_id` and `book_id` columns.
    # Each is an Integer ForeignKey (to members.id and books.id),
    # indexed and required.
    #
    # ---- WRITE YOUR CODE HERE (2 lines) ----

    member_id = Column(Integer, ForeignKey("members.id"), index=True, nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), index=True, nullable=False)

    # Task 3b: add the `member` and `book` relationships.
    # `member` back_populates the `loans` attribute (Task 3c).
    # `book` is one-directional - no back_populates needed.
    #
    # ---- WRITE YOUR CODE HERE (2 lines) ----
    member = relationship("Member", back_populates="loans")
    book = relationship("Book")

    # ...now scroll UP to the Member model and finish Task 3c!


# ===============================================================
# THE CHECKER - do not edit below this line
# ===============================================================

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    db = SessionLocal()
    rowling = Author(name="J.K. Rowling")
    db.add(rowling)
    db.commit()
    db.add_all([
        Book(title="Book One", author_id=rowling.id),
        Book(title="Book Two", author_id=rowling.id),
    ])
    db.commit()
    titles = [b.title for b in rowling.books]        # needs Task 1b
    assert titles == ["Book One", "Book Two"], "author.books is wrong"
    first = db.query(Book).first()
    assert first.author.name == "J.K. Rowling"        # needs Task 1c
    db.close()


def check_task_2():
    db = SessionLocal()
    sara = Member(name="Sara", email="sara@mail.com")
    db.add(sara)
    db.commit()
    db.add(LibraryCard(card_number="CARD-001", member_id=sara.id))
    db.commit()
    assert sara.card.card_number == "CARD-001", \
        "member.card should be ONE card object (did you set uselist=False?)"
    assert not isinstance(sara.card, list), \
        "member.card is a LIST - add uselist=False on Member.card"
    # The database must REJECT a second card for the same member:
    try:
        db.add(LibraryCard(card_number="CARD-002", member_id=sara.id))
        db.commit()
        raise AssertionError(
            "a second card was allowed - add unique=True to member_id!")
    except AssertionError:
        raise
    except Exception:
        db.rollback()  # IntegrityError = exactly what we want
    db.close()


def check_task_3():
    db = SessionLocal()
    omar = Member(name="Omar", email="omar@mail.com")
    book = db.query(Book).first()
    assert book is not None, "Task 1 must pass first"
    db.add(omar)
    db.commit()
    db.add(Loan(member_id=omar.id, book_id=book.id))
    db.commit()
    assert len(omar.loans) == 1, "member.loans is wrong (Task 3c?)"
    loan = omar.loans[0]
    assert loan.book.title == "Book One"              # needs Task 3b
    assert loan.member.name == "Omar"
    assert loan.returned is False, "returned should default to False"
    assert loan.borrowed_at is not None, "borrowed_at default missing"
    db.close()


print("\n--- Checking your lab ---")
check("Task 1: one-to-many  (Author -> Books)", check_task_1)
check("Task 2: one-to-one   (Member -> LibraryCard)", check_task_2)
check("Task 3: many-to-many (Member <-> Book via Loan)", check_task_3)

if all(results):
    print("\nALL TASKS PASS - you can model any relationship now!")
else:
    print(f"\n{results.count(True)}/3 tasks passing. "
          "Fix the first FAIL and run again.")
