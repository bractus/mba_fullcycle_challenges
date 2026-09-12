import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from src.ingest import ingest
from src.search import search

load_dotenv()

PROMPT_TEMPLATE = '''
CONTEXTO:
{resultados concatenados do banco de dados}

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
{pergunta do usuário}

RESPONDA A "PERGUNTA DO USUÁRIO"
'''

def get_llm_response(formatted_prompt: str) -> str:
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return "Erro: OPENAI_API_KEY não encontrada nas variáveis de ambiente."

        chat = ChatOpenAI(
            openai_api_key=api_key,
            model="gpt-4o-mini",
            temperature=0.0
        )
        response = chat.invoke(formatted_prompt)
        return response.content
    except Exception as e:
        return f"Erro ao se comunicar com o LLM: {e}"


def process_ingestion(file_path: str) -> str:

    if os.path.exists(file_path) and file_path.endswith('.pdf'):
        success = ingest(file_path)
        if success:
            return "Ingestão realizada com sucesso!"
        else:
            return "Falha na ingestão."
    else:
        return "Caminho inválido ou arquivo não é um PDF."


def ask_question(user_query: str) -> str:
    if not user_query:
        return ""

    # 1. Search
    search_results = search(user_query)
    
    if not search_results:
        return "Nenhuma informação relevante encontrada."
    
    if isinstance(search_results[0], str) and search_results[0].startswith("Error"):
            return search_results[0]

    # 2. Format Context
    context_text = ""
    for doc in search_results:
        # Add source metadata if available
        source = doc.metadata.get('source', 'desconhecido')
        page = doc.metadata.get('page', 'desconhecida')
        context_text += f"Fonte: {source} (Página {page})\nConteúdo: {doc.page_content}\n\n"
        
    # 3. Format Prompt
    final_prompt = PROMPT_TEMPLATE.replace("{resultados concatenados do banco de dados}", context_text)
    final_prompt = final_prompt.replace("{pergunta do usuário}", user_query)
    
    # 4. Generate Answer
    return get_llm_response(final_prompt)
