from fastapi import FastAPI

app = FastAPI(
    title="FastAPI Fundamentals API",
    description="A beginner-friendly FastAPI project setup tutorial.",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Welcome to FastAPI Fundamentals"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }
