import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama

load_dotenv()
CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_store")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

def query_documents(question):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
    retriever = vectordb.as_retriever(search_kwargs={"k": 4})

    llm = Ollama(model="llama3.2:1b", temperature=0.1, base_url=OLLAMA_HOST)

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    result = qa(question)
    print(f"\nAnswer:\n{result['result']}\n")
    print("Sources:")
    for doc in result["source_documents"]:
        print(f"- {doc.metadata.get('source')}")
