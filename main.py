from fastapi import FastAPI
from app.router.auth_router import router as auth_router
from app.router.user_router import router as user_router
from app.utils.init_db import create_tables
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app : FastAPI):
     # instialize DB at Start
     create_tables()
     yield # sepration point 


app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(auth_router)
app.include_router(user_router)

@app.get("/test")
def check():
    return {"status":'working'}