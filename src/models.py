import datetime
from jinja2 import FileSystemLoader
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, DateTime, LargeBinary, String
from sqlalchemy_file import FileField
from sqlalchemy_file.validators import ContentTypeValidator
from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import FileType

storage = FileSystemStorage(path="/src/media")

class BaseModel(DeclarativeBase):
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now())


class Document(BaseModel):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    filename = Column(String, index=True)
    
    def __str__(self):
        return f"{self.id}"




# alembic revision --autogenerate -m "Added quantity column"
# alembic upgrade head
