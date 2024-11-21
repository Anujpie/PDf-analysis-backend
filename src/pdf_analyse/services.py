from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from pinecone import ServerlessSpec
from src.config import settings
from langchain_community.embeddings import SentenceTransformerEmbeddings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
embeddings = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')

def create_index(name):

    for index in pc.list_indexes():
        if name in index["name"]:
            pc.delete_index(name)

    # Create a new index with dimension 384 using cosine similarity
    pc.create_index(name=name, dimension=384, metric="cosine", spec=ServerlessSpec(
        cloud='aws', 
        region='us-east-1'
    ))

    # Connect to the index
    index = pc.Index(name)

    return index.describe_index_stats()


def retrieve_from_pinecone(index_name, user_query="What information do you have on Instance Sync Permissions"):
    index = pc.Index(index_name)
    print("Index stats:", index.describe_index_stats())

    embeddings = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')
    pinecone = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embeddings)
    context = pinecone.similarity_search(user_query)[:5]
    
    return context

