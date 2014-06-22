#!/usr/bin/python3

import collections
import logging

Transition = collections.namedtuple("Transition", ["wchar", "move_head",
                                                   "new_state"])


class Tape(collections.defaultdict):
    def __init__(self, blank):
        super().__init__(lambda: blank)
        self.pos = 0
        self.blank = blank

    def __str__(self):
        ret = ""
        for k in range(min(self), max(self)+1):
            if k == self.pos:
                ret += "[{}]".format(str(self[k]))
            else:
                ret += str(self[k])

        return ret

    def move(self, movement):
        self.pos += movement

    def read(self):
        return self[self.pos]

    def write(self, char):
        self[self.pos] = char

    def read_vars(self, num):
        blanks_left = num - 1
        pos = self.pos
        ret = [""]
        while True:
            if self[pos] == self.blank:
                if blanks_left:
                    ret.append("")
                    blanks_left -= 1
                else:
                    return ret
            else:
                ret[-1] += self[pos]

            pos += 1


class TuringMachine:
    def __init__(self, tape, transitions, initial_state, accepting_states,
                 blank="b̸", outputs=1, loglevel=logging.WARNING):

        self.tape = Tape(blank)

        for i in range(len(tape)):
            self.tape[i] = tape[i]

        self._state = None
        self.states = set()
        self.state = initial_state
        self.accepting_states = accepting_states

        self.transitions = dict()
        for state, rchar, wchar, move_head, new_state in transitions:
            self.transitions.setdefault(state, {})[rchar] = Transition(
                wchar,
                move_head,
                new_state)

        self.outputs = outputs
        self.blank = blank

        logging.basicConfig(format='[{name}] [{levelname}] {message}', style="{",
                            level=loglevel)

        self.logger = logging.getLogger(self.__class__.__name__)

        self.logger.info("machine initialized. current state: {} {}".format(
            self.state, self.tape))

    def run(self):
        self.logger.info("machine started")
        while self.state not in self.accepting_states:
            self.step()

        self.logger.info("machine stopped")

    def step(self):
        transition = self.transitions[self.state][self.tape.read()]
        self.tape.write(transition.wchar)
        self.state = transition.new_state
        self.tape.move(transition.move_head)
        
        self.logger.info("step done. current state: {} {}".format(
            self.state, self.tape))

    def output(self):
        return self.tape.read_vars(self.outputs)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self.states.add(value)
        self._state = value
