#!/usr/bin/python3

from turing import TuringMachine
import logging
import argparse

def pos_int(val):
    try:
        val = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError("positive integer required") from None

    if val < 0:
        raise argparse.ArgumentTypeError("positive integer required")

    return val



parser = argparse.ArgumentParser()
parser.add_argument("a", type=pos_int)
parser.add_argument("b", type=pos_int)
parser.add_argument("-v", "--verbosity", action="count",
                    help="Increase verbosity")

args = parser.parse_args()
loglevel = {0: logging.WARNING,
            1: logging.INFO}.get(args.verbosity, logging.DEBUG)

logging.basicConfig(format='[{name}] [{levelname}] {message}',
                    style="{", level=loglevel)


a = "a"
q0 = "q₀"
q1 = "q₁"
q2 = "q₂"
q3 = "q₃"
q4 = "q₄"
q5 = "q₅"
qf = "qf"
blank = "b̸"

tape = [a] * args.a + [blank] + [a] * args.b

transitions = {(q0, a, a, 1, q0),
               (q0, blank, blank, 1, q1),
               (q1, a, a, 1, q2),
               (q1, blank, blank, 0, q2),
               (q2, blank, blank, -1, q3),
               (q2, a, a, 1, q2),
               (q3, a, blank, -1, q4),
               (q3, blank, blank, -1, q5),
               (q4, a, a, -1, q4),
               (q4, blank, a, -1, q5),
               (q5, a, a, -1, q5),
               (q5, blank, blank, 1, qf)}

machine = TuringMachine(tape, transitions, q0, {qf})
machine.run()
output = machine.output()
print(len(output[0]))
