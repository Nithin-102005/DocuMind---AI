from fastapi import FastAPI

app  = FastAPI(title="DocuMind AI API")

@app.get("/")
def root():
    return {
        "message" : "DocuMind AI API is running"
    }