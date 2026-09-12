import yaml
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

def init_dataset():
    import random
    from datasets import load_dataset
    from gepa.adapters.default_adapter.default_adapter import DefaultDataInst, EvaluationResult

    data = list(load_dataset("SWE-bench/SWE-bench_Verified", split="test"))
    data = [x for x in data if x.get("problem_statement")]

    examples: list[DefaultDataInst] = [
        {
            "input": x["problem_statement"],
            "additional_context": {
                "repo": x["repo"],
                "difficulty": str(x.get("difficulty", "")),
            },
            # placeholder — scoring is handled by UserStoryEvaluator, not ContainsAnswerEvaluator
            "answer": "User Story",
        }
        for x in data
    ][:120]

    random.Random(0).shuffle(examples)
    mid = len(examples) // 2
    return examples[:mid], examples[mid:], []


class UserStoryEvaluator:
    """Avalia se a resposta contém os elementos estruturais de uma User Story."""

    _MARKERS = ["Como", "para que", "Critérios de Aceitação", "Prioridade"]

    def __call__(self, data, response: str):
        from gepa.adapters.default_adapter.default_adapter import EvaluationResult

        hits = [m for m in self._MARKERS if m in response]
        score = len(hits) / len(self._MARKERS)
        missing = [m for m in self._MARKERS if m not in response]
        feedback = (
            f"{len(hits)}/{len(self._MARKERS)} elementos presentes."
            + (f" Faltando: {missing}." if missing else " User Story completa.")
        )
        return EvaluationResult(score=score, feedback=feedback)

load_dotenv()

import gepa

_root = Path(__file__).parents[2]
_prompts_dir = _root / "prompts"

_v1_path = _prompts_dir / "bug_to_user_story_v1.yml"
with open(_v1_path, "r", encoding="utf-8") as f:
    _yaml = yaml.safe_load(f)

system_prompt = _yaml["bug_to_user_story_v1"]["system_prompt"]

trainset, valset, _ = init_dataset()

seed_prompt = {"system_prompt": system_prompt}

result = gepa.optimize(
    seed_candidate=seed_prompt,
    trainset=trainset,
    valset=valset,
    task_lm="openrouter/openai/gpt-4o-mini",
    evaluator=UserStoryEvaluator(),
    max_metric_calls=150,
    reflection_lm="openrouter/openai/gpt-4o",
)

optimized_system_prompt = result.best_candidate["system_prompt"]
print("Optimized prompt:", optimized_system_prompt)

_output = {
    "bug_to_user_story_v4_gepa": {
        "description": "Prompt otimizado automaticamente pelo GEPA a partir do v1",
        "system_prompt": optimized_system_prompt,
        "user_prompt": "{bug_report}",
        "techniques_applied": [
            "gepa: otimização automática de prompt via busca evolutiva com reflexão",
            "seed baseado no v1: partida a partir do prompt original bug_to_user_story_v1",
        ],
        "version": "v4-gepa",
        "created_at": date.today().isoformat(),
        "tags": ["bug-analysis", "user-story", "product-management", "gepa", "auto-optimized"],
    }
}

_out_path = _prompts_dir / "bug_to_user_story_v4_gepa.yml"
with open(_out_path, "w", encoding="utf-8") as f:
    yaml.dump(_output, f, allow_unicode=True, sort_keys=False, indent=2)

print(f"Prompt salvo em: {_out_path}")
