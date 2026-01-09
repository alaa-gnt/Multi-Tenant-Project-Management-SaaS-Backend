from fastapi import FastAPI
from app.router.user_router import router as user_router

app = FastAPI()
app.include_router(user_router)

@app.get("/test")
def check():
    return {"status":'working'}