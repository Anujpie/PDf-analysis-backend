from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from src.routers import routers

app = FastAPI(debug=True, reload=True)
# app.mount("/static", StaticFiles(directory="src/static"), name="static")

origins = ["*"]

app.mount("/media", StaticFiles(directory="src/media"), name="media")

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins 
)

PREFIX = "/api/v1"

for router in routers:
    app.include_router(router, prefix=PREFIX)

