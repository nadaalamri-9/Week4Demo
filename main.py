import os

from fastapi import FastAPI
from dotenv import load_dotenv


load_dotenv()

app = FastAPI(title="Resume Evaluator API")

App_NAME = os.getenv("APP_NAME")

@app.get("/")
def root():
    return {"message":f"Resume Evaluator API is running, App name: {App_NAME}"}
