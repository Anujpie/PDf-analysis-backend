import os
from fastapi import FastAPI

MEDIA_FOLDER = os.path.join(os.path.dirname(__file__), "media")

def create_app():
    app = FastAPI()
    return app