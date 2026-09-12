"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import argparse
import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure
from langsmith import Client

load_dotenv()

USERNAME = os.getenv("USERNAME_LANGSMITH_HUB", "default_user")

def _build_template(prompt_data: dict) -> ChatPromptTemplate:
    """Converte o dict do YAML em ChatPromptTemplate."""
    messages = []
    if sp := prompt_data.get("system_prompt", "").strip():
        messages.append(("system", sp))
    messages.append(("human", prompt_data.get("user_prompt", "{input}")))
    return ChatPromptTemplate.from_messages(messages)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub.

    Usa o tenant_handle do workspace quando disponível (prompt público);
    caso contrário usa owner '-' que bypassa a checagem de tenant (privado).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    client = Client()
    try:
        settings = client._get_settings()
        handle = settings.tenant_handle or USERNAME

        # owner '-' bypassa o check de tenant; usar só quando handle não está configurado
        if settings.tenant_handle:
            full_name = f"{handle}/{prompt_name}"
            is_public = True
        else:
            full_name = prompt_name  # parse_prompt_identifier usa '-' como owner
            is_public = False
            print(
                f"⚠️  Workspace sem Hub handle configurado. "
                f"Publicando '{prompt_name}' como privado.\n"
                f"   Para publicar como público, acesse: https://smith.langchain.com/prompts"
            )

        template = _build_template(prompt_data)

        url = client.push_prompt(
            full_name,
            object=template,
            is_public=is_public,
            description=prompt_data.get("description", ""),
            tags=prompt_data.get("tags", []),
        )
        print(f"Prompt '{full_name}' publicado com sucesso! URL: {url}")
    except Exception as e:
        print(f"Erro ao fazer push do prompt '{prompt_name}': {e}")
        return False
    return True


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Push de prompts para o LangSmith Hub")
    parser.add_argument("--prompt_name", required=True, help="Nome do prompt a ser publicado")
    parser.add_argument("--prompt_file", required=True, help="Caminho do arquivo YAML com os dados do prompt")
    args = parser.parse_args()

    yaml_data = load_yaml(args.prompt_file)
    if yaml_data is None:
        return 1

    prompt_data = yaml_data.get(args.prompt_name, yaml_data)

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("Prompt inválido:")
        for error in errors:
            print(f"  - {error}")
        return 1

    return 0 if push_prompt_to_langsmith(args.prompt_name, prompt_data) else 1


if __name__ == "__main__":
    sys.exit(main())
