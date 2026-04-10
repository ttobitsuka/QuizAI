import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY が設定されていません。.env または環境変数を確認してください。"
    )

client = OpenAI(api_key=OPENAI_API_KEY)


SYSTEM_PROMPT = """
あなたは4択クイズ専用の判定器です。
与えられた問題文と4つの選択肢を読み、
各選択肢について以下をJSONのみで返してください。

- wrong_probability: その選択肢が誤答である確率 (0.0〜1.0)
- correct_probability: その選択肢が正答である確率 (0.0〜1.0)
- wrong_reason: 誤答らしさの短い理由
- correct_reason: 正答らしさの短い理由

制約:
- 必ずJSONのみを返すこと
- 配列の順番は入力順と一致させること
- 小数は0.0〜1.0の範囲にすること
- 正答確率と誤答確率は厳密な補数でなくてよい
- 知識に確信がない場合は、過信せず中間的な値にすること
"""

USER_TEMPLATE = """
問題:
{question}

選択肢:
{choices_text}

出力形式:
{{
  "items": [
    {{
      "choice_index": 0,
      "wrong_probability": 0.12,
      "correct_probability": 0.71,
      "wrong_reason": "短い理由",
      "correct_reason": "短い理由"
    }}
  ]
}}
"""


def _build_choices_text(choices: list[str]) -> str:
    return "\n".join([f"{idx}: {choice}" for idx, choice in enumerate(choices)])


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()

    # モデルが```json ... ```で返した場合の簡易対処
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSONの解析に失敗しました。response={text}") from e


def _clamp_probability(value: Any) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError) as e:
        raise ValueError(f"確率の値が不正です: {value}") from e

    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def score_choices(question: str, choices: list[str]) -> list[dict[str, Any]]:
    if len(choices) != 4:
        raise ValueError("choices は4個である必要があります。")

    user_prompt = USER_TEMPLATE.format(
        question=question,
        choices_text=_build_choices_text(choices),
    )

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    text = response.output_text
    data = _extract_json(text)

    items = data.get("items")
    if not isinstance(items, list) or len(items) != 4:
        raise ValueError(f"items の形式が不正です: {data}")

    normalized_items: list[dict[str, Any]] = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"item の形式が不正です: {item}")

        normalized_items.append(
            {
                "choice_index": idx,
                "choice_text": choices[idx],
                "wrong_probability": _clamp_probability(item.get("wrong_probability")),
                "correct_probability": _clamp_probability(item.get("correct_probability")),
                "wrong_reason": str(item.get("wrong_reason", "")),
                "correct_reason": str(item.get("correct_reason", "")),
            }
        )

    return normalized_items
