from dotenv import load_dotenv
from rag import RAGClass
import os

load_dotenv()  # This will load variables from the .env file into the environment

# Now you can access the API key
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the RAG class with the path to your data
rag = RAGClass(data_path="my_text_file.txt")

# Load and process documents
rag.load_documents()
rag.split_documents()
rag.create_vectorstore()
rag.setup_retriever()
rag.setup_qa_chain()

# Answer a sample query
rag.answer_query("What is Retrieval-Augmented Generation?")

# Evaluate the system with sample queries and ground truths
sample_queries = ["Define RAG.", "Explain vector databases."]
sample_ground_truths = ["Retrieval-Augmented Generation", "Vector databases store embeddings"]
rag.evaluate(sample_queries, sample_ground_truths)

