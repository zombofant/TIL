#!/usr/bin/python3
# encoding=utf-8
import abc
import collections
import logging
import re

syntax_var_assignment = re.compile(
    r"^x_?([0-9]+)\s*:=\s*x_?([0-9]+)(\s*([+-])\s*([0-9]+))?$")
syntax_const_assignment = re.compile(r"^x_?([0-9]+)\s*:=\s*([0-9]+)$")
syntax_loop = re.compile(r"^LOOP\s+x_?([0-9]+)\s+DO$")
syntax_while = re.compile(r"^WHILE\s+x_?([0-9]+)\s*(≠|!=)\s*0\s+DO$")
syntax_end = re.compile(r"^END$")
syntax_comment = re.compile(r"#.*$")

class VM(object):
    def __init__(self, *args):
        self._logger = logging.getLogger(type(self).__name__)
        self._data = collections.defaultdict(int)
        for i, arg in enumerate(args):
            self.set(i+1, max(int(arg), 0))

    def get(self, index):
        return self._data[index]

    def set(self, index, value):
        # print("x{} := {}".format(index, value))
        self._data[index] = int(value)

class Node(object):
    def __init__(self):
        super(Node, self).__init__()
        self._logger = logging.getLogger(type(self).__name__)

    @abc.abstractmethod
    def run(self, vm):
        pass

    @abc.abstractmethod
    def to_string(self, indent=""):
        pass

    def __str__(self):
        return self.to_string()

class BodyNode(Node):
    def __init__(self):
        super(BodyNode, self).__init__()
        self.body = []

    def run(self, vm):
        for stmt in self.body:
            stmt.run(vm)

    def to_string(self, indent=""):
        return "\n".join(
            stmt.to_string(indent=indent)
            for stmt in self.body)

class Program(BodyNode):
    pass

class Loop(BodyNode):
    @classmethod
    def parse(cls, line):
        m = syntax_loop.match(line)
        if not m:
            return None

        return cls(int(m.group(1)))

    def __init__(self, varindex):
        super(Loop, self).__init__()
        self._varindex = varindex

    def run(self, vm):
        n_iter = vm.get(self._varindex)
        self._logger.debug("LOOP x{n} DO  # x{n} = {v}".format(
            n=self._varindex,
            v=n_iter))
        for i in range(n_iter):
            self._logger.debug(".... x{n} DO  # k = {k}".format(
                n=self._varindex,
                k=i+1))
            super(Loop, self).run(vm)
        self._logger.debug("END LOOP x{n}".format(n=self._varindex))

    def to_string(self, indent=""):
        return """{indent}LOOP x{} DO
{}
{indent}END""".format(
    self._varindex,
    super(Loop, self).to_string(indent=indent+"    "),
    indent=indent)

class While(BodyNode):
    @classmethod
    def parse(cls, line):
        m = syntax_while.match(line)
        if not m:
            return None

        groups = m.groups()
        varindex = int(groups[0])
        return cls(varindex)

    def __init__(self, varindex):
        super(While, self).__init__()
        self._varindex = varindex

    def run(self, vm):
        self._logger.debug("WHILE x%d≠0 DO", self._varindex)
        currv = vm.get(self._varindex)
        while currv != 0:
            self._logger.debug("..... x{n} DO  # x{n} = {v}".format(
                n=self._varindex,
                v=currv))
            super(While, self).run(vm)
            currv = vm.get(self._varindex)

        self._logger.debug("END WHILE x{n}  # x{n} = {v}".format(
            n=self._varindex,
            v=currv))

    def to_string(self, indent=""):
        return """{indent}WHILE x{}≠0 DO
{}
{indent}END""".format(
    self._varindex,
    super(While, self).to_string(indent=indent+"    "),
    indent=indent)

class VarAssignment(Node):
    @classmethod
    def parse(cls, line):
        m = syntax_var_assignment.match(line)
        if not m:
            return None

        groups = m.groups()
        destindex = int(groups[0])
        srcindex = int(groups[1])
        if groups[2] is not None:
            offset = int(groups[3] + groups[4])
        else:
            offset = 0

        return cls(destindex, srcindex, offset)

    def __init__(self, destindex, srcindex, offset):
        super(VarAssignment, self).__init__()
        self._destindex = destindex
        self._srcindex = srcindex
        self._offset = offset

    def run(self, vm):
        s_value = vm.get(self._srcindex)
        new_value = max(s_value + self._offset, 0)
        self._logger.debug(
            "x%d := x%d %s %d  # x%d = %d, x%d := %d",
            self._destindex,
            self._srcindex,
            "+" if self._offset >= 0 else "-",
            abs(self._offset),
            self._srcindex,
            s_value,
            self._destindex,
            new_value)
        vm.set(self._destindex, new_value)

    def to_string(self, indent=""):
        return indent+"x{} := x{} {} {}".format(
            self._destindex,
            self._srcindex,
            "+" if self._offset >= 0 else "-",
            abs(self._offset))

class ConstAssignment(Node):
    @classmethod
    def parse(cls, line):
        m = syntax_const_assignment.match(line)
        if not m:
            return None

        groups = m.groups()
        destindex = int(groups[0])
        value = int(groups[1])

        return cls(destindex, value)

    def __init__(self, destindex, value):
        super(ConstAssignment, self).__init__()
        self._destindex = destindex
        self._value = value

    def run(self, vm):
        self._logger.debug(
            "x%d := %d",
            self._destindex,
            self._value)
        vm.set(self._destindex, self._value)

    def to_string(self, indent=""):
        return indent+"x{} := {}".format(
            self._destindex,
            self._value)

def parse(s, whilep=False):
    node_types = [
        Loop, VarAssignment, ConstAssignment
    ]
    if whilep:
        node_types.append(While)

    node_stack = []
    node = Program()
    lines = s.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # strip comments
        m = syntax_comment.search(line)
        if m is not None:
            line = line[:m.start()].strip()
        if not line:
            continue

        if syntax_end.match(line):
            node = node_stack.pop()
            continue

        for node_type in node_types:
            new_node = node_type.parse(line)
            if new_node is None:
                continue

            node.body.append(new_node)
            if isinstance(new_node, BodyNode):
                node_stack.append(node)
                node = new_node
            break
        else:
            raise ValueError("Invalid LOOP statement: {}".format(
                line))

    return node

if __name__ == "__main__":
    import argparse
    import os
    import sys

    def posint(v):
        v = int(v)
        if v < 0:
            raise ValueError("Must be a non-negative integer")
        return v

    parser = argparse.ArgumentParser(
        description="""Parse and interpret a LOOP or WHILE program, working in
        the space of natural numbers (including 0).""")
    parser.add_argument(
        "-f", "--infile",
        metavar="FILE",
        help="File containing the LOOP program to run. Omit to use STDIN.",
        type=argparse.FileType("r"),
        default=sys.stdin)
    parser.add_argument(
        "-d", "--dump",
        action="store_true",
        default=False,
        help="Dump the parsed program as text to STDOUT")
    parser.add_argument(
        "-r", "--run",
        metavar="ARG",
        nargs="*",
        type=int,
        help="Run the program, passing each argument as non-negative integer"
        " number to the variable slots starting from x_1 onwards. The result"
        " will be printed on STDOUT.")
    parser.add_argument(
        "-v",
        dest="verbosity",
        action="count",
        default=0,
        help="Increase verbosity of evaluation and parsing")
    parser.add_argument(
        "-w", "--while",
        dest="whilep",
        action="store_true",
        default=False,
        help="Interpret the input as WHILE program, instead of LOOP.")

    args = parser.parse_args()

    level = {
        0: logging.ERROR,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG
    }

    logging.basicConfig(
        level=level.get(args.verbosity, logging.DEBUG),
        format='{0}:%(levelname)-8s %(message)s'.format(
            os.path.basename(sys.argv[0])))


    try:
        program = parse(
            args.infile.read(),
            whilep=args.whilep)
    finally:
        if args.infile is not sys.stdin:
            args.infile.close()

    if args.dump:
        print(program)

    if args.run is not None:
        vm = VM(*args.run)
        program.run(vm)
        print(vm.get(0))
