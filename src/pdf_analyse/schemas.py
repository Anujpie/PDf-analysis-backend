from pydantic import BaseModel
from fastapi import File


class Documents(BaseModel):
    pdf_file = File


