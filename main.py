import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
from dfa import DFA
from nfa import NFA
from converter import convert_dfa_to_regex
from utils import parse_dfa_file, parse_nfa_file

class DFAtoRegexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DFA/NFA to Regular Expression Converter")

        # Flowchart input canvas
        self.canvas = tk.Canvas(root, width=600, height=400, bg='white')
        self.canvas.pack(pady=10)
        self.canvas.bind('<Button-1>', self.on_canvas_click)

        # State and transition management
        self.states = {}  # {state_id: (x, y, label)}
        self.transitions = []  # [(from_state, to_state, symbol)]
        self.start_state = None
        self.accept_states = set()
        self.state_counter = 0
        self.transition_mode = False
        self.transition_start = None
        self.automaton_type = "DFA"  # "DFA" or "NFA"

        # Mode selection
        mode_frame = tk.Frame(root)
        mode_frame.pack(pady=5)
        tk.Label(mode_frame, text="Automaton Type:").pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value="DFA")
        tk.Radiobutton(mode_frame, text="DFA", variable=self.mode_var, value="DFA", 
                      command=self.on_mode_change).pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="NFA", variable=self.mode_var, value="NFA", 
                      command=self.on_mode_change).pack(side=tk.LEFT)

        # Buttons for flowchart actions
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="Add State", command=self.add_state).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Draw Transition", command=self.toggle_transition_mode).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Set Start State", command=self.set_start_state).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Set Accept State", command=self.set_accept_state).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Convert to Regex", command=self.convert).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Load DFA from File", command=self.load_dfa_file).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Load NFA from File", command=self.load_nfa_file).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="NFA to DFA", command=self.nfa_to_dfa).pack(side=tk.LEFT, padx=5)

        # Output
        tk.Label(root, text="Regular Expression Output:").pack()
        self.output = scrolledtext.ScrolledText(root, height=4, width=50)
        self.output.pack()

    def on_mode_change(self):
        """Handle mode change between DFA and NFA"""
        self.automaton_type = self.mode_var.get()
        # Clear current automaton when switching modes
        self.clear_automaton()
        if self.automaton_type == "NFA":
            messagebox.showinfo("NFA Mode", "NFA mode allows multiple transitions from the same state on the same symbol.")
        else:
            messagebox.showinfo("DFA Mode", "DFA mode: each state has exactly one transition per symbol.")

    def clear_automaton(self):
        """Clear the current automaton"""
        self.canvas.delete("all")
        self.states.clear()
        self.transitions.clear()
        self.start_state = None
        self.accept_states.clear()
        self.state_counter = 0
        self.transition_start = None

    def on_canvas_click(self, event):
        if self.transition_mode:
            # In transition mode, first click selects start state, second click selects end state
            if self.transition_start is None:
                # Find the state clicked
                for state_id, (x, y, _) in self.states.items():
                    if abs(event.x - x) < 20 and abs(event.y - y) < 20:
                        self.transition_start = state_id
                        break
            else:
                # Find the end state
                for state_id, (x, y, _) in self.states.items():
                    if abs(event.x - x) < 20 and abs(event.y - y) < 20:
                        symbol = simpledialog.askstring("Transition Symbol", "Enter transition symbol:")
                        if symbol:
                            self.transitions.append((self.transition_start, state_id, symbol))
                            self.draw_transition(self.transition_start, state_id, symbol)
                        self.transition_start = None
                        break
        else:
            # In normal mode, clicking adds a new state
            self.add_state_at(event.x, event.y)

    def add_state(self):
        # Prompt for state label
        label = simpledialog.askstring("State Label", "Enter state label:")
        if label:
            self.add_state_at(300, 200, label)  # Default position

    def add_state_at(self, x, y, label=None):
        if label is None:
            label = f"q{self.state_counter}"
        self.states[self.state_counter] = (x, y, label)
        self.draw_state(self.state_counter)
        self.state_counter += 1

    def draw_state(self, state_id):
        x, y, label = self.states[state_id]
        self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill='white', outline='black')
        self.canvas.create_text(x, y, text=label)

    def toggle_transition_mode(self):
        self.transition_mode = not self.transition_mode
        if self.transition_mode:
            messagebox.showinfo("Transition Mode", "Click on a state to start drawing a transition, then click on another state to finish.")
        else:
            self.transition_start = None

    def draw_transition(self, from_state, to_state, symbol):
        from_x, from_y, _ = self.states[from_state]
        to_x, to_y, _ = self.states[to_state]
        # Draw an arrow from from_state to to_state
        self.canvas.create_line(from_x, from_y, to_x, to_y, arrow=tk.LAST)
        # Place the symbol label
        mid_x = (from_x + to_x) / 2
        mid_y = (from_y + to_y) / 2
        self.canvas.create_text(mid_x, mid_y, text=symbol)

    def set_start_state(self):
        # Prompt user to click on a state to set as start state
        messagebox.showinfo("Set Start State", "Click on a state to set as the start state.")
        self.root.bind('<Button-1>', self._on_set_start_state)

    def _on_set_start_state(self, event):
        for state_id, (x, y, _) in self.states.items():
            if abs(event.x - x) < 20 and abs(event.y - y) < 20:
                self.start_state = state_id
                self.canvas.create_text(x, y - 30, text="Start")
                break
        self.root.unbind('<Button-1>')

    def set_accept_state(self):
        # Prompt user to click on a state to set as accept state
        messagebox.showinfo("Set Accept State", "Click on a state to set as an accept state.")
        # Bind to canvas instead of root
        self.canvas.bind('<Button-1>', self._on_set_accept_state)

    def _on_set_accept_state(self, event):
        clicked_state = None
        for state_id, (x, y, _) in self.states.items():
            if abs(event.x - x) < 20 and abs(event.y - y) < 20:
                clicked_state = state_id
                break
        
        if clicked_state is not None:
            if clicked_state in self.accept_states:
                # Remove accept state
                self.accept_states.remove(clicked_state)
                # Remove the "Accept" label
                x, y, _ = self.states[clicked_state]
                for item in self.canvas.find_all():
                    if self.canvas.type(item) == "text":
                        coords = self.canvas.coords(item)
                        if abs(coords[0] - x) < 5 and abs(coords[1] - (y + 30)) < 5:
                            self.canvas.delete(item)
            else:
                # Add accept state
                self.accept_states.add(clicked_state)
                x, y, _ = self.states[clicked_state]
                self.canvas.create_text(x, y + 30, text="Accept")
        
        # Unbind the event
        self.canvas.unbind('<Button-1>')

    def _validate_transitions(self):
        # Ensure all transitions are 3-element tuples
        if not isinstance(self.transitions, list):
            raise ValueError("Transitions must be a list.")
        for t in self.transitions:
            if not (isinstance(t, tuple) and len(t) == 3):
                raise ValueError(f"Invalid transition tuple: {t}. Each transition must be a tuple (from_state, to_state, symbol)")

    def load_dfa_file(self):
        """Load DFA from file"""
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filepath:
            try:
                dfa = parse_dfa_file(filepath)
                self.automaton_type = "DFA"
                self.mode_var.set("DFA")
                self.load_automaton_from_object(dfa)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def load_nfa_file(self):
        """Load NFA from file"""
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filepath:
            try:
                nfa = parse_nfa_file(filepath)
                self.automaton_type = "NFA"
                self.mode_var.set("NFA")
                self.load_automaton_from_object(nfa)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def load_automaton_from_object(self, automaton):
        """Load automaton (DFA or NFA) from object"""
        # Clear current canvas and state
        self.clear_automaton()

        # Place states in a circle for visualization
        import math
        n = len(automaton.states)
        center_x, center_y, radius = 300, 200, 120
        angle_step = 2 * math.pi / n if n else 0
        state_positions = {}
        for i, label in enumerate(automaton.states):
            angle = i * angle_step
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.states[i] = (x, y, label)
            state_positions[label] = i
            self.draw_state(i)
            self.state_counter += 1

        # Draw transitions
        for (from_state, symbol), to_state in automaton.transitions.items():
            if isinstance(to_state, set):  # NFA case
                for target_state in to_state:
                    from_id = state_positions[from_state]
                    to_id = state_positions[target_state]
                    self.draw_transition(from_id, to_id, symbol)
            else:  # DFA case
                from_id = state_positions[from_state]
                to_id = state_positions[to_state]
                self.draw_transition(from_id, to_id, symbol)

        # Ensure self.transitions is correct for conversion
        self.transitions = []
        for (from_state, symbol), to_state in automaton.transitions.items():
            if isinstance(to_state, set):  # NFA case
                for target_state in to_state:
                    self.transitions.append((state_positions[from_state], state_positions[target_state], symbol))
            else:  # DFA case
                self.transitions.append((state_positions[from_state], state_positions[to_state], symbol))

        # Set start and accept states
        for i, (x, y, label) in self.states.items():
            if label == automaton.start_state:
                self.start_state = i
                self.canvas.create_text(x, y - 30, text="Start")
            if label in automaton.accept_states:
                self.accept_states.add(i)
                self.canvas.create_text(x, y + 30, text="Accept")

    def nfa_to_dfa(self):
        """Convert current NFA to DFA"""
        if self.automaton_type != "NFA":
            messagebox.showerror("Error", "Please load an NFA first.")
            return
        
        if not self.states or self.start_state is None or not self.accept_states or not self.transitions:
            messagebox.showerror("Error", "Please complete the NFA flowchart first.")
            return
        
        try:
            # Create NFA object from current state
            states = [self.states[state_id][2] for state_id in self.states]
            alphabet = list(set(symbol for _, _, symbol in self.transitions))
            start = self.states[self.start_state][2]
            accept = [self.states[state_id][2] for state_id in self.accept_states]
            transitions = [(self.states[from_state][2], symbol, self.states[to_state][2]) 
                          for from_state, to_state, symbol in self.transitions]
            
            nfa = NFA(states, alphabet, transitions, start, accept)
            dfa = nfa.to_dfa()
            
            # Display the converted DFA
            self.automaton_type = "DFA"
            self.mode_var.set("DFA")
            self.load_automaton_from_object(dfa)
            
            # Show conversion result
            result_text = f"NFA to DFA conversion completed!\n"
            result_text += f"Original NFA states: {len(states)}\n"
            result_text += f"Converted DFA states: {len(dfa.states)}\n"
            result_text += f"DFA states: {', '.join(dfa.states)}"
            
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, result_text)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def convert(self):
        """Convert current automaton to regular expression"""
        if not self.states or self.start_state is None or not self.accept_states or not self.transitions:
            messagebox.showerror("Error", "Please complete the automaton flowchart first.")
            return
        
        try:
            self._validate_transitions()
            print("self.transitions:", self.transitions)
            states = [self.states[state_id][2] for state_id in self.states]
            alphabet = list(set(symbol for _, _, symbol in self.transitions))
            start = self.states[self.start_state][2]
            accept = [self.states[state_id][2] for state_id in self.accept_states]
            transitions = [(self.states[from_state][2], symbol, self.states[to_state][2]) 
                          for from_state, to_state, symbol in self.transitions]
            
            if self.automaton_type == "NFA":
                # Convert NFA to DFA first, then to regex
                nfa = NFA(states, alphabet, transitions, start, accept)
                dfa = nfa.to_dfa()
                regex = convert_dfa_to_regex(dfa)
                result_text = f"NFA converted to DFA, then to regex:\n{regex}"
            else:
                # Direct DFA to regex conversion
                print("DEBUG: Accept state IDs from GUI:", self.accept_states)
                print("DEBUG: Accept state labels for DFA:", accept)
                dfa = DFA(states, alphabet, list(transitions), start, accept)
                regex = convert_dfa_to_regex(dfa)
                result_text = f"DFA to regex:\n{regex}"
            
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, result_text)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = DFAtoRegexApp(root)
    root.mainloop()