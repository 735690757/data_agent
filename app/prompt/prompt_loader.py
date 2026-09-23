# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 20:18
# @Author : KarryLiu
# File : prompt_loader
# @Project : data_agent
from pathlib import Path


def load_prompt(name: str):
    prompt_path = Path(__file__).parents[2] / "prompts" / f"{name}.prompt"

    return prompt_path.read_text(encoding="utf-8")
