from selector import select_answer


def test_keeps_at_least_two_choices():
    choices = ["A", "B", "C", "D"]
    wrong_probs = [0.95, 0.91, 0.88, 0.05]
    correct_probs = [0.05, 0.10, 0.20, 0.90]

    result = select_answer(
        choices=choices,
        wrong_probs=wrong_probs,
        correct_probs=correct_probs,
        wrong_threshold=0.75,
        keep_threshold=0.30,
        low_conf_threshold=0.40,
    )

    assert len(result["remaining_indices"]) >= 2
    assert len(result["eliminated_indices"]) <= 2


def test_no_elimination_when_low_confidence():
    choices = ["A", "B", "C", "D"]
    wrong_probs = [0.20, 0.30, 0.25, 0.35]
    correct_probs = [0.21, 0.33, 0.29, 0.31]

    result = select_answer(
        choices=choices,
        wrong_probs=wrong_probs,
        correct_probs=correct_probs,
        wrong_threshold=0.75,
        keep_threshold=0.30,
        low_conf_threshold=0.40,
    )

    assert result["mode"] == "no_elimination_low_confidence"
    assert result["eliminated_indices"] == []
    assert result["remaining_indices"] == [0, 1, 2, 3]
    assert result["selected_index"] == 1


def test_eliminates_only_high_wrong_and_low_correct_choices():
    choices = ["A", "B", "C", "D"]
    wrong_probs = [0.80, 0.20, 0.78, 0.10]
    correct_probs = [0.15, 0.60, 0.25, 0.70]

    result = select_answer(
        choices=choices,
        wrong_probs=wrong_probs,
        correct_probs=correct_probs,
        wrong_threshold=0.75,
        keep_threshold=0.30,
        low_conf_threshold=0.40,
    )

    assert result["mode"] == "elimination"
    assert set(result["eliminated_indices"]) == {0, 2}
    assert set(result["remaining_indices"]) == {1, 3}
    assert result["selected_index"] == 3


def test_does_not_eliminate_if_correct_probability_is_too_high():
    choices = ["A", "B", "C", "D"]
    wrong_probs = [0.85, 0.10, 0.20, 0.30]
    correct_probs = [0.55, 0.40, 0.35, 0.25]

    result = select_answer(
        choices=choices,
        wrong_probs=wrong_probs,
        correct_probs=correct_probs,
        wrong_threshold=0.75,
        keep_threshold=0.30,
        low_conf_threshold=0.40,
    )

    assert 0 not in result["eliminated_indices"]


def test_selects_highest_correct_probability_among_remaining():
    choices = ["A", "B", "C", "D"]
    wrong_probs = [0.90, 0.20, 0.10, 0.85]
    correct_probs = [0.10, 0.65, 0.72, 0.15]

    result = select_answer(
        choices=choices,
        wrong_probs=wrong_probs,
        correct_probs=correct_probs,
        wrong_threshold=0.75,
        keep_threshold=0.30,
        low_conf_threshold=0.40,
    )

    assert set(result["remaining_indices"]) == {1, 2}
    assert result["selected_index"] == 2
    assert result["selected_choice"] == "C"


def test_no_elimination_mode_when_no_candidate_matches_rule():
    choices = ["A", "B", "C", "D"]
    wrong_probs = [0.40, 0.50, 0.35, 0.60]
    correct_probs = [0.20, 0.55, 0.45, 0.70]

    result = select_answer(
        choices=choices,
        wrong_probs=wrong_probs,
        correct_probs=correct_probs,
        wrong_threshold=0.75,
        keep_threshold=0.30,
        low_conf_threshold=0.40,
    )

    assert result["mode"] == "no_elimination"
    assert result["eliminated_indices"] == []
    assert result["selected_index"] == 3
