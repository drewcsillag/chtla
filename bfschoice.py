from typing import Callable, List, TypeVar

T = TypeVar("T")


class BfsException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Chooser(object):
    def __init__(self, executions: List[List[int]], prechosen: List[int]):
        self.executions = executions
        self.prechosen = prechosen
        self.index = 0
        self.newChoices: List[int] = []

    def choose_index(self, numArgs: int) -> int:
        if self.index < len(self.prechosen):
            retind = self.prechosen[self.index]
            self.index += 1
            return retind

        for i in range(numArgs):
            newExecution = self.prechosen + self.newChoices + [i]
            # print("New execution: " + str(newExecution))
            self.executions.append(newExecution)
            # print("exes now: " + str(self.executions))

        raise BfsException("BOOP!")

    def choose(self, args: List[T]) -> T:
        try:
            index = self.choose_index(len(args))
            return args[index]
        except IndexError:
            print("trying index %d of %r" % (index, args))
            raise

    def pick(self, l: List[T]) -> T:
        c = self.choose_index(len(l))
        ret = l[c]
        # print("pick from [" + str(" ".join([str(i)for i in l])) + "]")
        # print ("chose index " + str(c) + " value " + str(ret))

        del l[c]
        return ret

    def stop(self) -> None:
        self.executions[:] = []


def run_choices(fn: Callable[[Chooser], None]) -> None:
    executions: List[List[int]] = [[]]
    while executions:
        # print("executions is: " + str(executions))
        try:
            e = executions[0]
            executions = executions[1:]
            fn(Chooser(executions, e))
        except BfsException:
            pass


# ct  = 0
# def b(c):
#     global ct
#     ct += 1
#     print("C -> " + str(ct))
#     print("%d %d %d" % (c.choose_index(2),c.choose_index(2),c.choose_index(2)))

# run_choices(b)
