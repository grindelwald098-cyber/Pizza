from fastapi import FastAPI

app = FastAPI(title="Pizza API")


@app.get("/")
def root():
    return {"status": "ok"}
