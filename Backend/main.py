from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
import subprocess
import os
from agent import run_tailor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JDRequest(BaseModel):
    job_description: str

@app.get("/")
def root():
    return {"status": "Resume Tailor Agent running"}

@app.post("/tailor")
def tailor_resume(request: JDRequest):
    result = run_tailor(request.job_description)
    return {
        "latex": result["latex"],
        "message": result["agent_response"]
    }

@app.get("/download")
def download_resume():
    if os.path.exists("output_resume.tex"):
        return FileResponse(
            "output_resume.tex",
            media_type="application/x-tex",
            filename="Anagha_Kalyanaraman_Resume.tex"
        )
    return {"error": "No resume generated yet"}