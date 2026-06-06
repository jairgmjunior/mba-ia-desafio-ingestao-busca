# Desafio MBA Engenharia de Software com IA - Full Cycle

Sistema de ingestão e busca semântica sobre um PDF usando LangChain, PostgreSQL e pgVector.

## Pré-requisitos

- Python 3.11 a 3.13 (recomendado)
- Docker e Docker Compose
- Chave de API da [OpenAI](https://platform.openai.com/) **ou** [Google Gemini](https://aistudio.google.com/)

> Se `pip install -r requirements.txt` falhar por incompatibilidade de versão, use Python 3.12 ou instale manualmente:
>
> `pip install langchain langchain-community langchain-openai langchain-google-genai langchain-postgres langchain-text-splitters python-dotenv pypdf psycopg psycopg-binary`

## Configuração

1. Clone o repositório e entre na pasta do projeto.

2. Crie e ative o ambiente virtual:

```bash
python -m venv venv
```

Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Copie o arquivo de ambiente e configure sua chave de API:

Linux/macOS:

```bash
cp .env.example .env
```

Windows (PowerShell):

```powershell
Copy-Item .env.example .env
```

Edite o `.env` e preencha `OPENAI_API_KEY` (recomendado) ou `GOOGLE_API_KEY`. Se ambas estiverem definidas, a OpenAI terá prioridade.

> **Importante:** coloque a chave de API somente no `.env`. Nunca commite credenciais no `.env.example` ou em outros arquivos versionados.

5. Coloque o PDF na raiz do projeto com o nome `document.pdf` (ou ajuste `PDF_PATH` no `.env`).

## Execução

Execute os comandos abaixo a partir da raiz do projeto.

### 1. Subir o banco de dados

```bash
docker compose up -d
```

Aguarde o PostgreSQL ficar saudável. O serviço `bootstrap_vector_ext` cria a extensão `vector` automaticamente.

### 2. Ingerir o PDF

```bash
python src/ingest.py
```

O script divide o PDF em chunks de 1000 caracteres (overlap de 150), gera embeddings e salva no pgVector. A collection é recriada a cada execução.

### 3. Rodar o chat

```bash
python src/chat.py
```

Exemplo de interação:

```
Faça sua pergunta:

PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.

PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

Digite `sair`, `exit` ou `quit` para encerrar.

## Estrutura do projeto

```
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── src/
│   ├── ingest.py    # Ingestão do PDF
│   ├── search.py    # Busca vetorial e prompt da LLM
│   └── chat.py      # CLI de interação
├── document.pdf     # PDF para ingestão
└── README.md
```

## Modelos utilizados

| Provedor | Embeddings             | LLM                    |
|----------|------------------------|------------------------|
| OpenAI   | text-embedding-3-small | gpt-5-nano             |
| Gemini   | models/embedding-001   | gemini-2.5-flash-lite  |

Os modelos podem ser alterados no arquivo `.env`.

## Fluxo da aplicação

1. **Ingestão:** o PDF é lido, dividido em chunks, convertido em embeddings e armazenado no PostgreSQL com pgVector.
2. **Busca:** a pergunta do usuário é vetorizada e os 10 chunks mais relevantes são recuperados (`k=10`).
3. **Resposta:** os chunks são enviados como contexto para a LLM, que responde estritamente com base no conteúdo recuperado.
