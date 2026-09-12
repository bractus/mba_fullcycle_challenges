# RAG Chat System

Este projeto é um sistema de **RAG (Retrieval-Augmented Generation)** simples via linha de comando (CLI), desenvolvido em Python. Ele permite a ingestão de documentos PDF em um banco de dados vetorial (PostgreSQL com pgvector) e oferece uma interface de chat para responder perguntas com base no conteúdo desses documentos.

## Funcionalidades

*   **Ingestão de PDF:** Processa arquivos PDF, divide o texto em "chunks" e armazena os vetores de embedding no banco de dados.
*   **Busca Semântica:** Utiliza busca vetorial para encontrar trechos relevantes nos documentos ingeridos.
*   **Chat Inteligente:** Responde perguntas do usuário utilizando um LLM (GPT-4o-mini via OpenAI), fundamentando as respostas estritamente no contexto recuperado do banco de dados.
*   **Banco de Dados:** Utiliza PostgreSQL com a extensão `pgvector` para armazenamento eficiente dos embeddings.

## Estrutura do Projeto

*   `main.py`: Ponto de entrada da aplicação CLI. Gerencia o fluxo de ingestão e o loop de chat.
*   `src/ingest.py`: Lógica para carregamento de PDF, divisão de texto e inserção no banco vetorial.
*   `src/search.py`: Lógica para realizar a busca por similaridade no banco de dados.
*   `src/chat.py`: Contém o template de prompt utilizado para instruir o LLM.
*   `docker-compose.yml`: Configuração dos serviços Docker (PostgreSQL com pgvector).

## Pré-requisitos

*   Docker e Docker Compose
*   Python 3.10+
*   Chave de API da OpenAI (para acesso aos modelos LLM e Embeddings)

## Instalação e Configuração

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-repositorio>
    cd desafio_mba
    ```

2.  **Configure as variáveis de ambiente:**
    Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
    ```env
    OPENAI_API_KEY=sua_chave_aqui
    DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
    PG_VECTOR_COLLECTION_NAME=document_embeddings
    OPENAI_EMBEDDING_MODEL=text-embedding-3-small
    ```

3.  **Inicie o banco de dados:**
    Execute o comando abaixo para subir o container do PostgreSQL com pgvector:
    ```bash
    docker-compose up -d
    ```

4.  **Crie e ative o ambiente virtual (Recomendado):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Linux/Mac
    # .venv\Scripts\activate   # Windows
    ```

5.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

## Como Usar

1.  **Execute a aplicação:**
    ```bash
    python main.py
    ```

2.  **Ingestão de Documentos:**
    *   Ao iniciar, o sistema perguntará se você deseja ingerir um arquivo PDF.
    *   Digite `s` e forneça o caminho completo para o arquivo PDF (ex: `/Users/nome/documento.pdf`).
    *   O sistema processará o arquivo e salvará os embeddings no banco.

3.  **Chat:**
    *   Após a ingestão (ou se pular essa etapa), você entrará no modo de chat.
    *   Digite sua pergunta e pressione Enter.
    *   O sistema buscará informações relevantes nos documentos ingeridos e gerará uma resposta.
    *   Para sair, digite `sair` ou `exit`.

## Tecnologias Utilizadas

*   **LangChain:** Framework para orquestração de LLMs e acesso a dados.
*   **PostgreSQL + pgvector:** Banco de dados relacional com suporte a vetores para busca semântica.
*   **OpenAI Embeddings:** Modelo `text-embedding-3-small` para gerar vetores.
*   **OpenAI Chat:** Modelo `gpt-4o-mini` para geração de respostas.