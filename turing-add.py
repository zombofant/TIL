#!/usr/bin/python3

from turing import TuringMachine
import logging

a = "a"
q0 = "q₀"
q1 = "q₁"
q2 = "q₂"
q3 = "q₃"
q4 = "q₄"
q5 = "q₅"
qf = "qf"
blank = "b̸"

tape = [a, a, blank, a]

transitions = {(q0, a, a, 1, q0),
               (q0, blank, blank, 1, q1),
               (q1, a, a, 1, q2),
               (q1, blank, blank, 0, q2),
               (q2, blank, blank, -1, q3),
               (q2, a, a, 1, q2),
               (q3, a, blank, -1, q4),
               (q4, a, a, -1, q4),
               (q4, blank, a, -1, q5),
               (q5, a, a, -1, q5),
               (q5, blank, blank, 1, qf)}

machine = TuringMachine(tape, transitions, q0, {qf}, loglevel=logging.DEBUG)
machine.run()
print(machine.output())
