from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

def ingest(pdf_path: str) -> bool:
        
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

        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,        
            chunk_overlap=200,      
        )

        chunks = text_splitter.split_documents(documents)

        vector_store = PGVector.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=COLLECTION_NAME,
            connection=CONNECTION,
            use_jsonb=True,  
            pre_delete_collection=False,  
        )
    except Exception as e:
        print(f"Error: {e}")
        return False

    return True
