import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/rag",
)
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME", "documents")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-5-nano")
GOOGLE_EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")
GOOGLE_LLM_MODEL = os.getenv("GOOGLE_LLM_MODEL", "gemini-2.5-flash-lite")

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


def get_embeddings():
    if os.getenv("OPENAI_API_KEY"):
        return OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)

    if os.getenv("GOOGLE_API_KEY"):
        return GoogleGenerativeAIEmbeddings(model=GOOGLE_EMBEDDING_MODEL)

    return None


def get_llm():
    if os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model=OPENAI_LLM_MODEL, temperature=0)

    if os.getenv("GOOGLE_API_KEY"):
        return ChatGoogleGenerativeAI(model=GOOGLE_LLM_MODEL, temperature=0)

    return None


def get_vector_store(*, pre_delete_collection: bool = False) -> PGVector | None:
    embeddings = get_embeddings()
    if not embeddings:
        print("Defina OPENAI_API_KEY ou GOOGLE_API_KEY no arquivo .env")
        return None

    return PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
        pre_delete_collection=pre_delete_collection,
    )


def search_prompt(question=None):
    vector_store = get_vector_store()
    llm = get_llm()

    if not vector_store or not llm:
        return None

    def ask(pergunta: str) -> str:
        results = vector_store.similarity_search_with_score(pergunta, k=10)
        contexto = "\n\n".join(doc.page_content for doc, _ in results)
        prompt = PROMPT_TEMPLATE.format(contexto=contexto, pergunta=pergunta)
        response = llm.invoke(prompt)
        return response.content

    if question is not None:
        return ask(question)

    return ask
