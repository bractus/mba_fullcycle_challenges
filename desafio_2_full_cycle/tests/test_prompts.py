"""
Testes automatizados para validação de prompts.
Executa em todos os arquivos YAML da pasta prompts/.
"""
import pytest
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_all_prompts():
    """Retorna pytest.param(prompt_data, id=chave) para cada prompt nos YAMLs."""
    params = []
    for path in sorted(PROMPTS_DIR.glob("*.yml")):
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            for key, prompt_data in data.items():
                params.append(pytest.param(prompt_data, id=key))
    return params


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("prompt", load_all_prompts())
def test_prompt_has_system_prompt(prompt):
    """Verifica se o campo 'system_prompt' existe e não está vazio."""
    assert "system_prompt" in prompt, "Campo 'system_prompt' não encontrado"
    assert prompt["system_prompt"].strip(), "Campo 'system_prompt' está vazio"


@pytest.mark.parametrize("prompt", load_all_prompts())
def test_prompt_has_role_definition(prompt):
    """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
    system_prompt = prompt.get("system_prompt", "")
    role_markers = ["Você é", "você é", "You are", "you are"]
    assert any(m in system_prompt for m in role_markers), (
        "system_prompt não define uma persona. "
        "Esperado algo como 'Você é um Product Owner...'"
    )


@pytest.mark.parametrize("prompt", load_all_prompts())
def test_prompt_mentions_format(prompt):
    """Verifica se o prompt exige formato Markdown ou User Story padrão."""
    system_prompt = prompt.get("system_prompt", "")
    format_markers = [
        "User Story",
        "user story",
        "Markdown",
        "**",       # markdown bold — indica saída estruturada
        "###",
    ]
    assert any(m in system_prompt for m in format_markers), (
        "system_prompt não menciona nenhum formato esperado "
        "(User Story, Markdown ou elementos de estrutura como '**')."
    )


@pytest.mark.parametrize("prompt", load_all_prompts())
def test_prompt_has_few_shot_examples(prompt):
    """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot).

    Critério: ao menos dois blocos 'Relato de Bug:' no texto (um por exemplo),
    ou presença do marcador 'Resposta:' que delimita a saída esperada nos exemplos.
    """
    system_prompt = prompt.get("system_prompt", "")
    has_resposta = "Resposta:" in system_prompt
    has_multiple_inputs = system_prompt.count("Relato de Bug:") >= 2
    assert has_resposta or has_multiple_inputs, (
        "system_prompt não contém exemplos few-shot. "
        "Adicione ao menos um par entrada/saída usando os marcadores "
        "'Relato de Bug:' e 'Resposta:'."
    )


@pytest.mark.parametrize("prompt", load_all_prompts())
def test_prompt_no_todos(prompt):
    """Garante que não há marcadores [TODO] ou TODO no texto do prompt."""
    system_prompt = prompt.get("system_prompt", "")
    user_prompt = prompt.get("user_prompt", "")
    for field, content in [("system_prompt", system_prompt), ("user_prompt", user_prompt)]:
        assert "TODO" not in content, f"'{field}' contém marcador TODO não resolvido"
        assert "[TODO]" not in content, f"'{field}' contém marcador [TODO] não resolvido"


@pytest.mark.parametrize("prompt", load_all_prompts())
def test_minimum_techniques(prompt):
    """Verifica se ao menos 2 técnicas estão listadas nos metadados do YAML."""
    techniques = prompt.get("techniques_applied", [])
    assert len(techniques) >= 2, (
        f"Mínimo de 2 técnicas requeridas em 'techniques_applied', "
        f"encontradas: {len(techniques)}. "
        "Adicione as técnicas utilizadas (ex: few-shot, CoT, role prompting)."
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
