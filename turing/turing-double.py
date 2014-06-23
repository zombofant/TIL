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
parser.add_argument("-v", "--verbosity", action="count",
                    help="Increase verbosity")

args = parser.parse_args()
loglevel = {0: logging.WARNING,
            1: logging.INFO,
            2: logging.DEBUG}.get(args.verbosity)


a = "a"
b = "b"
c = "c"

r = 1
n = 0
l = -1

q0 = "q₀"
q1 = "q₁"
q2 = "q₂"
q3 = "q₃"
q4 = "q₄"
stop = "stop"
bl = "b̸"

tape = [a] * args.a

transitions = {(q0, bl, bl, n, stop),
               (q0, a, b, r, q1),
               (q1, a, a, r, q1),
               (q1, c, c, r, q1),
               (q1, bl, c, n, q2),
               (q2, c, c, l, q2),
               (q2, a, a, l, q2),
               (q2, b, b, r, q0),
               (q0, c, c, r, q3),
               (q3, c, c, r, q3),
               (q3, bl, bl, l, q4),
               (q4, c, a, l, q4),
               (q4, b, a, l, q4),
               (q4, bl, bl, r, stop)}

machine = TuringMachine(tape, transitions, q0, {stop}, loglevel=loglevel)
machine.run()
output = machine.output()
print(len(output[0]))
