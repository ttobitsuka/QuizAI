from typing import Any


def select_answer(
    choices: list[str],
    wrong_probs: list[float],
    correct_probs: list[float],
    wrong_threshold: float = 0.75,
    keep_threshold: float = 0.30,
    low_conf_threshold: float = 0.40,
) -> dict[str, Any]:
    """
    ルール:
    1. 全体的に正答確信が低ければ除外しない
    2. W_i >= wrong_threshold かつ C_i <= keep_threshold の選択肢を除外候補
    3. ただし最低2個は残す
    4. 残った選択肢の中で C_i 最大を選ぶ
    """

    n = len(choices)

    if n != 4:
        raise ValueError("choices は4個である必要があります。")
    if len(wrong_probs) != n or len(correct_probs) != n:
        raise ValueError("wrong_probs / correct_probs の長さが choices と一致していません。")

    # 全体的に確信が低い場合は、除外せずそのまま最大Cを選ぶ
    max_correct = max(correct_probs)
    if max_correct < low_conf_threshold:
        selected_index = correct_probs.index(max_correct)
        return {
            "mode": "no_elimination_low_confidence",
            "eliminated_indices": [],
            "remaining_indices": list(range(n)),
            "selected_index": selected_index,
            "selected_choice": choices[selected_index],
        }

    # 除外候補
    elimination_candidates = [
        i
        for i in range(n)
        if wrong_probs[i] >= wrong_threshold and correct_probs[i] <= keep_threshold
    ]

    # 誤答確率が高い順に並べる
    elimination_candidates = sorted(
        elimination_candidates,
        key=lambda i: wrong_probs[i],
        reverse=True,
    )

    # 最低2個残す
    max_eliminate = n - 2
    eliminated_indices = elimination_candidates[:max_eliminate]

    remaining_indices = [i for i in range(n) if i not in eliminated_indices]

    # 念のため安全装置
    if len(remaining_indices) < 2:
        eliminated_indices = []
        remaining_indices = list(range(n))

    # 残った中で正答確率最大
    selected_index = max(remaining_indices, key=lambda i: correct_probs[i])

    mode = "elimination" if eliminated_indices else "no_elimination"

    return {
        "mode": mode,
        "eliminated_indices": eliminated_indices,
        "remaining_indices": remaining_indices,
        "selected_index": selected_index,
        "selected_choice": choices[selected_index],
    }
