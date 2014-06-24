#!/usr/bin/python3
import ast
import logging
import re

typeline = re.compile(r"^type\s*:\s*(.*?)$", re.I)
inputline = re.compile(r"^input\s*:\s*(([^,]+)(,\s*([^,]+))*)$", re.I)
outputline = re.compile(r"^output\s*:\s*(([^,]+)(,\s*([^,]+))*)$", re.I)
finalline = re.compile(r"^final\s*:\s*(([^,]+)(,\s*([^,]+)\s*)*)$", re.I)
startline = re.compile(r"^start\s*:\s*(.*)\s*$", re.I)

class TransformNamesToStr(ast.NodeTransformer):
    def visit_Name(self, node):
        return ast.Str(
            node.id,
            lineno=node.lineno,
            col_offset=node.col_offset)

class Natural:
    @classmethod
    def to_turing_input(cls, value):
        value = int(value)
        if value < 0:
            raise ValueError("invalid natural: {}".format(value))

        return value

    @classmethod
    def from_turing_output(cls, value):
        return value

    def __str__(self):
        return "natural"

class Unary:
    def __init__(self):
        self.char = "a"

    def process_args(self, args):
        if not args:
            return args

        if args[0] == "char":
            if len(args) < 2:
                raise ValueError("missing argument after char")
            char = args[1]
            if len(char) > 1:
                raise ValueError("unary character must be length 1")
            self.char = args[1]
            args = args[2:]
        return args

    def to_turing_input(self, value):
        return self.char * value

    def from_turing_output(self, value):
        return len(value)

    def __str__(self):
        return "unary char {}".format(self.char)

class TypeChain:
    def __init__(self, *types):
        self.types = list(types)

    def to_turing_input(self, value):
        for type_ in self.types:
            value = type_.to_turing_input(value)
        return value

    def from_turing_output(self, value):
        for type_ in reversed(self.types):
            value = type_.from_turing_output(value)
        return value

    def __str__(self):
        return "{}".format(
            " ".join(self.types[1:] + self.types[0]))

types = {
    "natural": Natural
}

transforms = {
    "unary": Unary
}

def parse_type(typetuple):
    typetuple = [
        s for s in (s.strip() for s in typetuple) if s
    ]

    if not typetuple:
        raise ValueError("Types must not be empty")

    typename = typetuple[-1]
    try:
        chain = [types[typename.lower()]()]
    except KeyError as err:
        raise ValueError("Unknown type: {}".format(typename))

    typeargs = typetuple[:-1]
    while typeargs:
        try:
            qualifier = transforms[typeargs[0].lower()]()
        except KeyError as err:
            raise ValueError("Unknown type qualifier (or invalid argument to"
                             " previous qualifier): {}".format(
                                 typeargs[0]))
        try:
            typeargs = qualifier.process_args(typeargs[1:])
        except ValueError as err:
            raise ValueError("Invalid argument to {} qualifier: {}".format(
                typeargs[0],
                err))
        chain.append(qualifier)

    return TypeChain(*chain)


def parse_machine(lines, blank):
    transitions = set()

    machine_type = None
    input_signature = None
    output_signature = None
    final_states = None
    initial_state = None

    def set_type(m):
        nonlocal machine_type

        if machine_type is not None:
            raise ValueError("Multiple type directives")

        machine_type = tuple(m.group(1).lower().split())

    def set_input_signature(m):
        nonlocal input_signature

        if input_signature is not None:
            raise ValueError("Multiple input signatures")

        input_signature = [
            tuple(item.strip().split(" "))
            for item in m.group(1).split(",")
        ]

    def set_output_signature(m):
        nonlocal output_signature

        if output_signature is not None:
            raise ValueError("Multiple output signatures")

        output_signature = [
            tuple(item.strip().split(" "))
            for item in m.group(1).split(",")
        ]

    def set_final_states(m):
        nonlocal final_states

        if final_states is not None:
            raise ValueError("Multiple final state directives")

        final_states = m.group(1).split(",")

    def set_initial_state(m):
        nonlocal initial_state

        if initial_state is not None:
            raise ValueError("Multiple start state directives")

        initial_state = m.group(1)

    def get_transition(line):
        line = line.rstrip(",")

        try:
            transition = compile(
                line,
                "",
                "eval",
                ast.PyCF_ONLY_AST).body
        except SyntaxError:
            raise ValueError("Not a valid transition line")

        if not isinstance(transition, ast.Tuple):
            raise ValueError("Top level transition element must be a tuple")

        transition = TransformNamesToStr().visit(transition)
        transition = ast.Expression(
            transition,
            lineno=0,
            col_offset=0)
        transition_code = compile(transition, "", "eval")
        transition = eval(transition_code, {}, {})

        return transition

    linetypes = {
        typeline: set_type,
        inputline: set_input_signature,
        outputline: set_output_signature,
        finalline: set_final_states,
        startline: set_initial_state,
    }

    for line in lines:
        hashpos = line.find("#")
        if hashpos >= 0:
            line = line[:hashpos]
        line = line.strip()
        if not line:
            continue

        for linetype, processor in linetypes.items():
            m = linetype.match(line)
            if m is None:
                continue

            processor(m)
            break
        else:
            try:
                transition = get_transition(line)
            except ValueError as err:
                raise ValueError("Unparsable line: `{}` ({}, and not a valid directive)".format(line, err))

            transitions.add(transition)

    input_signature = list(map(parse_type, input_signature))
    output_signature = list(map(parse_type, output_signature))

    if machine_type != ("dtm", "function"):
        raise ValueError("unsupported machine type: {}".format(
            " ".join(machine_type)))

    if machine_type is None:
        raise ValueError("Missing type directive")
    if input_signature is None:
        raise ValueError("Missing input directive")
    if output_signature is None:
        raise ValueError("Missing output directive")
    if initial_state is None:
        raise ValueError("Missing start directive")
    if final_states is None:
        raise ValueError("Missing final directive")

    direction_map = {
        "n": 0,
        "l": -1,
        "r": 1
    }

    def map_char(char):
        if char == "blank":
            return blank
        elif len(char) > 1:
            raise ValueError("Characters must be of length 1")
        return char

    try:
        transitions = [
            (qp, map_char(r), map_char(w), direction_map[direction], qn)
            for qp, r, w, direction, qn in transitions]
    except KeyError as err:
        raise ValueError("Unknown direction: {}".format(str(err)[1:-1]))


    return (machine_type, input_signature, output_signature, transitions,
            initial_state, final_states)

if __name__ == "__main__":
    import argparse
    import os
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        default=0,
        action="count",
        help="Increase verbosity, up to three times",
        dest="verbosity")
    parser.add_argument(
        "-b",
        dest="blank",
        default="X",
        help="Blank symbol. By default, this is X"
        )
    parser.add_argument(
        "infile",
        help="File containing the machine definition"
        )
    parser.add_argument(
        "args",
        nargs="*",
        help="Arguments to pass to the turing machine. The semantics"
             "of this depend on the type of the machine")

    args = parser.parse_args()

    loglevel = {
        0: logging.ERROR,
        1: logging.WARNING,
        2: logging.INFO
    }.get(args.verbosity, logging.DEBUG)

    logging.basicConfig(
        format='{0}:%(levelname)-8s %(message)s'.format(
            os.path.basename(sys.argv[0])),
        level=loglevel
    )

    if len(args.blank) != 1:
        raise ValueError("Blank must have a length of exactly 1")

    with open(args.infile, "r") as f:
        lines = f.readlines()

    (machine_type,
     input_signature,
     output_signature,
     transitions,
     initial_state,
     final_states) = parse_machine(lines, args.blank)

    import turing

    if len(input_signature) != len(args.args):
        raise ValueError("Turing machine expects {} input(s), but {}"
                         " given".format(len(input_signature),
                                         len(args.args)))

    initial_tape = args.blank.join(
        inputtype.to_turing_input(arg)
        for arg, inputtype in zip(args.args, input_signature))

    machine = turing.TuringMachine(
        initial_tape,
        transitions,
        initial_state,
        final_states,
        blank=args.blank,
        outputs=len(output_signature))

    try:
        machine.run()
    except ValueError as err:
        print("In state {}:".format(machine.state))
        print(err)
        sys.exit(1)

    for value, outputtype in zip(machine.output(), output_signature):
        print(outputtype.from_turing_output(value))
