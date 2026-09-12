from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

def search(query: str) -> list:
        
    API_KEY = os.getenv('OPENAI_API_KEY')
    CONNECTION = os.getenv("DATABASE_URL")
    COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")

    try:
        embeddings = OpenAIEmbeddings(
            openai_api_key=API_KEY,
            model="text-embedding-3-small"
        )

        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=COLLECTION_NAME,
            connection=CONNECTION,
            use_jsonb=True,
        )

        return vector_store.similarity_search(query, k=10)  

    except Exception as e:
        return [f"Error: {e}"]
