"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header
from langsmith import Client

load_dotenv()

USERNAME = os.getenv("USERNAME_LANGSMITH_HUB", "default_user")

def pull_prompts_from_langsmith(prompt_name: str):
    client = Client()
    try:
        prompt = client.pull_prompt(USERNAME+'/'+prompt_name)
    except Exception as e:
        print(f"Erro ao puxar prompt '{prompt_name}': {e}")
        sys.exit(1)
    return prompt


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Pull de prompts do LangSmith Hub")
    parser.add_argument("--prompt_name", required=True, help="Nome do prompt a ser baixado")
    args = parser.parse_args()

    prompt = pull_prompts_from_langsmith(args.prompt_name)
    print(f"PROMPT: {prompt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
