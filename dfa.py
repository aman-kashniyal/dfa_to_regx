class DFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = sorted([s.strip() for s in states])
        self.alphabet = sorted([a.strip() for a in alphabet])
        self.start_state = start_state.strip()
        self.accept_states = sorted([a.strip() for a in accept_states])
        # Only build dict if transitions is a list (of 3-tuples)
        if isinstance(transitions, list):
            self.transitions = self.build_transition_dict(transitions)
        else:
            self.transitions = transitions
        self.validate()

    def build_transition_dict(self, transitions):
        transition_dict = {}
        for from_state, symbol, to_state in transitions:
            from_state = from_state.strip()
            to_state = to_state.strip()
            symbol = symbol.strip()
            if (from_state, symbol) in transition_dict:
                raise ValueError(f"Non-deterministic transition: {from_state} on {symbol}")
            transition_dict[(from_state, symbol)] = to_state
        return transition_dict

    def validate(self):
        if isinstance(self.transitions, dict):
            items = self.transitions.items()
        elif isinstance(self.transitions, list):
            items = [((from_state, symbol), to_state) for from_state, symbol, to_state in self.transitions]
        else:
            raise ValueError("Unknown transitions type: " + str(type(self.transitions)))
        
        if self.start_state not in self.states:
            raise ValueError(f"Start state {self.start_state} not in states list")
        for state in self.accept_states:
            if state not in self.states:
                raise ValueError(f"Accept state {state} not in states list")
        for (from_state, symbol), to_state in items:
            if from_state not in self.states or to_state not in self.states:
                raise ValueError(f"Transition {from_state}→{to_state} uses undefined states")
            if symbol not in self.alphabet:
                raise ValueError(f"Symbol {symbol} not in alphabet")

    def get_transitions(self):
        return [(from_s, sym, to_s) for (from_s, sym), to_s in self.transitions.items()]