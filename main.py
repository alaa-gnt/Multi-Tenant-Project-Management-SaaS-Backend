from fastapi import FastAPI

app = FastAPI()

@app.get("/test")
def check():
    return {"status":'working'}