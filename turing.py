#!/usr/bin/python3

import collections
import pprint


Transition = collections.namedtuple("Transition", ["wchar", "move_head",
                                                   "new_state"])


class TuringMachine:
    def __init__(self, tape, transitions, initial_state, accepting_states,
                 blank=None, outputs=1):

        self.tape = collections.defaultdict(lambda: blank)

        for i in range(len(tape)):
            self.tape[i] = tape[i]

        self._state = None
        self.states = set()
        self.state = initial_state
        self.pos = 0
        self.accepting_states = accepting_states

        self.transitions = dict()
        for state, rchar, wchar, move_head, new_state in transitions:
            self.transitions.setdefault(state, {})[rchar] = Transition(
                wchar,
                move_head,
                new_state)

        self.outputs = outputs
        self.blank = blank

    def run(self):
        while self.state not in self.accepting_states:
            self.step()

    def step(self):
        transition = self.transitions[self.state][self.tape[self.pos]]
        self.tape[self.pos] = transition.wchar
        self.state = transition.new_state
        self.pos += transition.move_head

    def output(self):
        blanks_left = self.outputs - 1
        pos = self.pos
        ret = [""]
        while True:
            if self.tape[pos] == self.blank:
                if blanks_left:
                    ret.append("")
                else:
                    return ret
            else:
                ret[-1] += self.tape[self.pos]
            
            pos += 1

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value not in self.states:
            self.states.add(value)

        self._state = value


a = "a"
q0 = "q₀"
q1 = "q₁"
q2 = "q₂"
q3 = "q₃"
q4 = "q₄"
q5 = "q₅"
qf = "qf"

tape = [a, a,None,a]

transitions = {(q0, a, a, 1, q0),
               (q0, None, None, 1, q1),
               (q1, a, a, 1, q2),
               (q1, None, None, 0, q2),
               (q2, None, None, -1, q3),
               (q2, a, a, 1, q2),
               (q3, a, None, -1, q4),
               (q4, a, a, -1, q4),
               (q4, None, a, -1, q5),
               (q5, a, a, -1, q5),
               (q5, None, None, 1, qf)}

machine = TuringMachine(tape, transitions, q0, {qf})
print(str(machine.tape))
pprint.pprint(machine.transitions)
print("running machine")
machine.run()
print(machine.output())


