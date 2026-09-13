from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello World"}


@app.get("/health")
def check_health():
    return {"status": "200 OK", "message": "KyraIO - AI Operations Copilot is running"}


@app.post("/conversations")
def create_conversation():
    pass
