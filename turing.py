#!/usr/bin/python3

import collections


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
                    blanks_left -= 1
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
        self.states.add(value)
        self._state = value
