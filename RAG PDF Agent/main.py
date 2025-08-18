import argparse
from ingest import ingest_documents
from response import query_documents

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resume/Transcript RAG CLI Tool")
    parser.add_argument("--ingest", action="store_true", help="Ingest documents into ChromaDB")
    parser.add_argument("--query", type=str, help="Ask a question about the documents")
    args = parser.parse_args()

    if args.ingest:
        ingest_documents()
    elif args.query:
        query_documents(args.query)
    else:
        parser.print_help()