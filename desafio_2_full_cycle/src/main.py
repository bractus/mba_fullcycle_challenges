"""
Avalia todos os prompts da pasta /prompts usando evaluate.py.

Fluxo:
1. Descobre automaticamente todos os prompts em /prompts/*.yml
2. Cria/reutiliza o dataset de avaliação no LangSmith
3. Avalia cada prompt contra o dataset
4. Exibe resultados individuais e tabela comparativa final
"""

import os
import sys
import yaml
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

from evaluate import create_evaluation_dataset, evaluate_prompt, display_results
from utils import check_env_vars, print_section_header

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
DATASET_PATH = Path(__file__).parent.parent / "datasets" / "bug_to_user_story.jsonl"


def discover_prompts(username: str) -> list[tuple[str, str]]:
    """Retorna (hub_name, local_key) para cada prompt encontrado em /prompts."""
    entries = []
    for path in sorted(PROMPTS_DIR.glob("*.yml")):
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            for key in data:
                entries.append((f"{username}/{key}", key))
    return entries


def print_summary(results: list[dict]) -> None:
    print_section_header("RESUMO COMPARATIVO")

    col_name = 42
    print(f"{'Prompt':<{col_name}} {'Help':>6} {'Corr':>6} {'F1':>6} {'Clar':>6} {'Prec':>6}  Status")
    print("-" * (col_name + 42))

    for r in results:
        s = r["scores"]
        name = r["name"].split("/")[-1]  # exibe só o nome sem o username
        if s:
            status = "✅ OK" if r["passed"] else "❌ FAIL"
            print(
                f"{name:<{col_name}}"
                f"{s.get('helpfulness', 0):>6.2f}"
                f"{s.get('correctness', 0):>6.2f}"
                f"{s.get('f1_score', 0):>6.2f}"
                f"{s.get('clarity', 0):>6.2f}"
                f"{s.get('precision', 0):>6.2f}"
                f"  {status}"
            )
        else:
            print(f"{name:<{col_name}}{'N/A':>6}{'N/A':>6}{'N/A':>6}{'N/A':>6}{'N/A':>6}  ❌ ERR")

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    print(f"\nTotal: {total} | Aprovados: {passed} | Reprovados: {total - passed}")


def main() -> int:
    print_section_header("AVALIAÇÃO DE TODOS OS PROMPTS")

    provider = os.getenv("LLM_PROVIDER", "openrouter")

    required_vars = ["LANGSMITH_API_KEY", "LLM_PROVIDER", "USERNAME_LANGSMITH_HUB"]
    if provider == "openrouter":
        required_vars.append("OPENROUTER_API_KEY")
    elif provider == "openai":
        required_vars.append("OPENAI_API_KEY")
    elif provider in ["google", "gemini"]:
        required_vars.append("GOOGLE_API_KEY")

    if not check_env_vars(required_vars):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")
    project_name = os.getenv("LANGSMITH_PROJECT", "prompt-optimization")

    if not DATASET_PATH.exists():
        print(f"❌ Dataset não encontrado: {DATASET_PATH}")
        return 1

    client = Client()
    dataset_name = f"{project_name}-eval"
    create_evaluation_dataset(client, dataset_name, str(DATASET_PATH))

    prompts = discover_prompts(username)
    if not prompts:
        print("❌ Nenhum prompt encontrado em /prompts")
        return 1

    print(f"\nPrompts descobertos ({len(prompts)}):")
    for hub_name, _ in prompts:
        print(f"  - {hub_name}")
    print()

    results = []
    for hub_name, _ in prompts:
        try:
            scores = evaluate_prompt(hub_name, dataset_name, client)
            passed = display_results(hub_name, scores)
            results.append({"name": hub_name, "scores": scores, "passed": passed})
        except Exception as e:
            print(f"\n❌ Falha ao avaliar '{hub_name}': {e}")
            results.append({"name": hub_name, "scores": {}, "passed": False})

    print_summary(results)

    all_passed = all(r["passed"] for r in results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
