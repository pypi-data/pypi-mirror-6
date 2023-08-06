from collections import namedtuple, defaultdict
from random import Random

ProgramStep = namedtuple(
    "ProgramStep",
    ("definitions", "arguments", "operation")
)

Consume = namedtuple("Consume", ("varstack",))


def consume(varstack):
    return Consume(varstack)


def requirements(argspec):
    result = {}
    for x in argspec:
        if isinstance(x, Consume):
            x = x.varstack
        result[x] = result.get(x, 0) + 1
    return result


class TestMachineError(Exception):
    pass


class VarStack(object):
    def __init__(self, name, context):
        self.name = name
        self.context = context
        self.data = []
        self.names = []

    def _integrity_check(self):
        assert len(self.data) == len(self.names)

    def pop(self, i=0):
        i = -1 - i
        self._integrity_check()
        result = self.data[i]
        self.context.on_read(self.names[i])
        del self.data[i]
        del self.names[i]
        return result

    def push(self, head):
        self._integrity_check()
        self.data.append(head)
        v = self.context.newvar()
        self.names.append(v)
        self.context.on_write(v)

    def dup(self):
        self._integrity_check()
        self.names.append(self.names[-1])
        self.data.append(self.data[-1])

    def peek(self, index=0):
        self._integrity_check()
        i = -1 - index
        self.context.on_read(self.names[i])
        return self.data[i]

    def has(self, count):
        self._integrity_check()
        return len(self.data) >= count

    def size(self):
        return len(self.data)


class RunContext(object):
    def __init__(self, random=None, simulation=False):
        self.random = random or Random()
        self.varstacks = {}
        self.var_index = 0
        self.reset_tracking()
        self.log = []
        self.simulation = simulation

    def reset_tracking(self):
        self.values_read = []
        self.values_written = []

    def run_program(self, program):
        for operation in program:
            self.execute(operation)

    def heights(self):
        result = {}
        for k, s in self.varstacks.items():
            result[k] = s.size()
        return result

    def execute(self, operation):
        self.reset_tracking()
        try:
            if self.simulation:
                operation.simulate(self)
            else:
                operation.invoke(self)

            self.log.append(ProgramStep(
                operation=operation,
                definitions=tuple(self.values_written),
                arguments=tuple(self.values_read)
            ))
        except Exception:
            self.log.append(ProgramStep(
                operation=operation,
                definitions=(),
                arguments=tuple(self.values_read)
            ))
            raise

    def __repr__(self):
        return "RunContext(%s)" % (
            ', '.join(
                "%s=%r" % (v.name, len(v.data))
                for v in self.varstacks.values()
            )
        )

    def newvar(self):
        self.var_index += 1
        return "t%d" % (self.var_index,)

    def on_read(self, var):
        self.values_read.append(var)

    def on_write(self, var):
        self.values_written.append(var)

    def varstack(self, name):
        if isinstance(name, Consume):
            name = name.varstack
        try:
            return self.varstacks[name]
        except KeyError:
            varstack = VarStack(name, self)
            self.varstacks[name] = varstack
            return varstack

    def read(self, argspec):
        result = []
        seen = defaultdict(lambda: 0)
        for a in argspec:
            varstack = self.varstack(a)
            if isinstance(a, Consume):
                v = varstack.pop(seen[a.varstack])
            else:
                v = varstack.peek(seen[a])
                seen[a] += 1
            result.append(v)
        return tuple(result)
