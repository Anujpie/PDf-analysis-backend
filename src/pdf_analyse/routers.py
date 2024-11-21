import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session

from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src import MEDIA_FOLDER
from src.models import Document
from src.base.custom_renderer import CustomJSONResponse

from src.database import get_db
from src.pdf_analyse.services import create_index, delete_file_from_system, retrieve_from_pinecone

router = APIRouter(
    prefix="/file",
    tags=['pdf_analyse']
)
index_name = "test"

llm = ChatOllama(model="llama3", temperature=0)

@router.get('/get', response_class=CustomJSONResponse)
async def get_file(response: Response, db: Session = Depends(get_db)):
    """ Get all files """
    
    documents = db.query(Document).all()
    return documents


@router.post('/upload', response_class=CustomJSONResponse)
async def file_upload(files: List[UploadFile], response: Response, db: Session = Depends(get_db)):
    """ Upload multiple files """
    
    for file in files:
        print('file: ', file)
        try:
            file_path = os.path.join(MEDIA_FOLDER, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
            # file_content = await file.read()
            document = Document(filename=file.filename)

            db.add(document)
            db.commit()
            db.refresh(document)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {e}")

    response = {"message": "Files are uploaded"}
    return response


@router.post('/train', response_class=CustomJSONResponse)
async def file_train(response: Response, db: Session = Depends(get_db)):
    """" Train uploaded PDFs and create embedding in pinecone DB. Lastly delete all files from system and database records. """

    create_index(index_name)
    documents = db.query(Document).all()
    
    for document in documents:
        file_path = os.path.join(MEDIA_FOLDER, document.filename)

        if not os.path.exists(file_path):
            continue

        loader = PyPDFLoader(file_path)
        data = loader.load()

        # Split the document into smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        fragments = text_splitter.split_documents(data)
        
        # Print a sample of the text fragments
        print("Fragments sample:", fragments[:3])

        embeddings = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')

        # Convert fragments into embeddings and store in Pinecone
        PineconeVectorStore.from_documents(
            fragments, embeddings, index_name=index_name
        )

        delete_file_from_system(file_path)
        db.delete(document)
    
    db.commit()

    response = {"message": "Files are trained"}
    return response


@router.get('/chat', response_class=CustomJSONResponse)
async def get_response(user_query: str, response: Response, db: Session = Depends(get_db)):
    """ Provide any context and model will give you response based on PDF. 
    If context is not available in PDF, it gives you general response based on trained data on the model. """

    context = retrieve_from_pinecone(index_name, user_query)[:5]

    template = """
        Answer the question below according to your knowledge in a way that will be helpful to students asking the question.
        The following context is your only source of knowledge to answer from.
        Context: {context}
        User question: {user_question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    return chain.stream({
        "context": context,
        "user_question": user_query
    })


