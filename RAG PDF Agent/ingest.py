import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()
DATA_DIR = os.getenv("DATA_DIR", "data")
CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_store")

def ingest_documents():
    docs = []
    for file in os.listdir(DATA_DIR):
        if file.lower().endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(DATA_DIR, file))
            docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )
    vectordb.persist()
    print(f"Ingested {len(chunks)} chunks into ChromaDB at '{CHROMA_DIR}'")