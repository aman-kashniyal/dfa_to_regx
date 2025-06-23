from dfa import DFA
from collections import defaultdict, deque

class NFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = [s.strip() for s in states]
        self.alphabet = [a.strip() for a in alphabet]
        self.start_state = start_state.strip()
        self.accept_states = [a.strip() for a in accept_states]
        
        # Build transition function: {(state, symbol): set of states}
        self.transitions = self.build_transition_dict(transitions)
        self.validate()
    
    def build_transition_dict(self, transitions):
        """Convert list of transitions to dictionary format for NFA"""
        transition_dict = defaultdict(set)
        for from_state, symbol, to_state in transitions:
            from_state = from_state.strip()
            to_state = to_state.strip()
            symbol = symbol.strip()
            transition_dict[(from_state, symbol)].add(to_state)
        return transition_dict
    
    def validate(self):
        """Validate the NFA structure"""
        if self.start_state not in self.states:
            raise ValueError(f"Start state {self.start_state} not in states list")
        for state in self.accept_states:
            if state not in self.states:
                raise ValueError(f"Accept state {state} not in states list")
        for (from_state, symbol), to_states in self.transitions.items():
            if from_state not in self.states:
                raise ValueError(f"Transition from undefined state: {from_state}")
            if symbol not in self.alphabet and symbol != 'ε':
                raise ValueError(f"Symbol {symbol} not in alphabet")
            for to_state in to_states:
                if to_state not in self.states:
                    raise ValueError(f"Transition to undefined state: {to_state}")
    
    def epsilon_closure(self, states):
        """Compute ε-closure of a set of states"""
        closure = set(states)
        stack = list(states)
        
        while stack:
            state = stack.pop()
            # Get all states reachable via ε-transitions from current state
            epsilon_transitions = self.transitions.get((state, 'ε'), set())
            for next_state in epsilon_transitions:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        
        return closure
    
    def move(self, states, symbol):
        """Compute the set of states reachable from given states on input symbol"""
        result = set()
        for state in states:
            transitions = self.transitions.get((state, symbol), set())
            result.update(transitions)
        return result
    
    def to_dfa(self):
        """Convert NFA to DFA using subset construction"""
        # Initialize with start state's ε-closure
        initial_states = self.epsilon_closure({self.start_state})
        initial_state_name = self.state_set_to_name(initial_states)
        
        # Track DFA states and transitions
        dfa_states = {initial_state_name}
        dfa_transitions = {}
        unprocessed_states = deque([(initial_state_name, initial_states)])
        
        while unprocessed_states:
            dfa_state_name, nfa_states = unprocessed_states.popleft()
            
            for symbol in self.alphabet:
                # Compute next states for this symbol
                next_nfa_states = self.move(nfa_states, symbol)
                if next_nfa_states:
                    # Compute ε-closure of the result
                    next_nfa_states = self.epsilon_closure(next_nfa_states)
                    next_dfa_state_name = self.state_set_to_name(next_nfa_states)
                    
                    # Add transition
                    dfa_transitions[(dfa_state_name, symbol)] = next_dfa_state_name
                    
                    # Add new state if not seen before
                    if next_dfa_state_name not in dfa_states:
                        dfa_states.add(next_dfa_state_name)
                        unprocessed_states.append((next_dfa_state_name, next_nfa_states))
        
        # Determine accept states
        dfa_accept_states = []
        for dfa_state_name in dfa_states:
            nfa_states = self.name_to_state_set(dfa_state_name)
            if any(state in self.accept_states for state in nfa_states):
                dfa_accept_states.append(dfa_state_name)
        
        # Convert transitions to list format for DFA constructor
        dfa_transitions_list = []
        for (from_state, symbol), to_state in dfa_transitions.items():
            dfa_transitions_list.append((from_state, symbol, to_state))
        
        return DFA(list(dfa_states), self.alphabet, dfa_transitions_list, 
                  initial_state_name, dfa_accept_states)
    
    def state_set_to_name(self, states):
        """Convert a set of NFA states to a DFA state name"""
        if not states:
            return "DEAD"
        sorted_states = sorted(list(states))
        return "{" + ",".join(sorted_states) + "}"
    
    def name_to_state_set(self, state_name):
        """Convert a DFA state name back to a set of NFA states"""
        if state_name == "DEAD":
            return set()
        # Remove braces and split by comma
        states_str = state_name.strip("{}")
        if not states_str:
            return set()
        return set(states_str.split(","))
    
    def get_transitions(self):
        """Get transitions as a list of 3-tuples"""
        transitions = []
        for (from_state, symbol), to_states in self.transitions.items():
            for to_state in to_states:
                transitions.append((from_state, symbol, to_state))
        return transitions 