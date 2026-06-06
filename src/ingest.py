import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

from search import get_vector_store


def resolve_pdf_path() -> Path:
    pdf_path = os.getenv("PDF_PATH", "document.pdf")
    path = Path(pdf_path)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


def ingest_pdf():
    pdf_path = resolve_pdf_path()

    if not pdf_path.exists():
        print(f"PDF não encontrado: {pdf_path}")
        return

    vector_store = get_vector_store(pre_delete_collection=True)
    if not vector_store:
        return

    loader = PyPDFLoader(str(pdf_path))
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )
    chunks = text_splitter.split_documents(documents)

    vector_store.add_documents(chunks)
    print(f"Ingestão concluída: {len(chunks)} chunks salvos a partir de {pdf_path.name}")


if __name__ == "__main__":
    ingest_pdf()
