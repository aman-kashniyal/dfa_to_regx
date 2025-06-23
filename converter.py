def convert_dfa_to_regex(dfa):
    import copy

    # Step 0: Check if DFA has at least one accepting state
    if not dfa.accept_states:
        return "No accepting paths"

    # Step 1: Setup GNFA with new START and END states
    states = copy.deepcopy(dfa.states)
    new_start = "START"
    new_end = "END"

    while new_start in states or new_end in states:
        new_start += "_"
        new_end += "_"

    states = [new_start] + states + [new_end]
    transitions = {}

    # Initialize all transitions to ∅ (empty)
    for s1 in states:
        for s2 in states:
            transitions[(s1, s2)] = "∅"

    # Add DFA transitions
    for (from_state, symbol), to_state in dfa.transitions.items():
        key = (from_state, to_state)
        if transitions[key] != "∅":
            transitions[key] = f"({transitions[key]}+{symbol})"
        else:
            transitions[key] = symbol

    # Add ε transitions from new start and to new end
    transitions[(new_start, dfa.start_state)] = "ε"
    for accept_state in dfa.accept_states:
        transitions[(accept_state, new_end)] = "ε"

    # Step 2: Eliminate all intermediate states except new_start and new_end
    intermediate_states = [s for s in states if s not in [new_start, new_end]]

    for state in intermediate_states:
        loop = transitions.get((state, state), "∅")
        loop_expr = f"({loop})*" if loop != "∅" else ""

        for i in states:
            if i == state:
                continue
            in_label = transitions.get((i, state), "∅")
            if in_label == "∅":
                continue

            for j in states:
                if j == state:
                    continue
                out_label = transitions.get((state, j), "∅")
                if out_label == "∅":
                    continue

                mid_expr = f"{in_label}{loop_expr}{out_label}"
                current = transitions.get((i, j), "∅")

                if current == "∅":
                    transitions[(i, j)] = mid_expr
                else:
                    transitions[(i, j)] = f"({current}+{mid_expr})"

        # Remove transitions involving the eliminated state
        for s in states:
            transitions.pop((s, state), None)
            transitions.pop((state, s), None)

    # Step 3: Final expression from new_start to new_end
    regex = transitions.get((new_start, new_end), "∅")
    if regex == "∅":
        return "No accepting paths"
    return regex
