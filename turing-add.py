#!/usr/bin/python3

from turing import TuringMachine
import pprint

a = "a"
q0 = "q₀"
q1 = "q₁"
q2 = "q₂"
q3 = "q₃"
q4 = "q₄"
q5 = "q₅"
qf = "qf"

tape = [a, a, None, a]

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
