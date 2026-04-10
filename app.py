import argparse
import json
import sys

from scorer import score_choices
from selector import select_answer


def solve_quiz(question: str, choices: list[str]) -> dict:
    scores = score_choices(question=question, choices=choices)

    wrong_probs = [item["wrong_probability"] for item in scores]
    correct_probs = [item["correct_probability"] for item in scores]

    result = select_answer(
        choices=choices,
        wrong_probs=wrong_probs,
        correct_probs=correct_probs,
        wrong_threshold=0.75,
        keep_threshold=0.30,
        low_conf_threshold=0.40,
    )

    output = {
        "question": question,
        "choices": choices,
        "scores": scores,
        "decision": result,
        "selected_choice": choices[result["selected_index"]],
    }
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="4択クイズ用AI: 誤答確率/正答確率を用いて回答するCLI"
    )
    parser.add_argument("--question", type=str, required=True, help="問題文")
    parser.add_argument(
        "--choices",
        type=str,
        nargs=4,
        required=True,
        help="4つの選択肢を順番に指定してください",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="見やすい形式で出力する",
    )

    args = parser.parse_args()

    try:
        result = solve_quiz(question=args.question, choices=args.choices)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if args.pretty:
        print("\n=== 問題 ===")
        print(result["question"])

        print("\n=== 選択肢 ===")
        for idx, choice in enumerate(result["choices"]):
            print(f"{idx}: {choice}")

        print("\n=== スコア ===")
        for idx, item in enumerate(result["scores"]):
            print(
                f"{idx}: "
                f"W={item['wrong_probability']:.3f}, "
                f"C={item['correct_probability']:.3f}, "
                f"wrong_reason={item['wrong_reason']}, "
                f"correct_reason={item['correct_reason']}"
            )

        print("\n=== 判定 ===")
        print(f"mode: {result['decision']['mode']}")
        print(f"eliminated_indices: {result['decision']['eliminated_indices']}")
        print(f"remaining_indices: {result['decision']['remaining_indices']}")
        print(f"selected_index: {result['decision']['selected_index']}")
        print(f"selected_choice: {result['selected_choice']}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
