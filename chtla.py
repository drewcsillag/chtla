from typing import Optional, Callable, List, Any, TypeVar, Tuple
from choice import Chooser, run_choices

T = TypeVar("T")


def check_assertions(which, invariants):
    for invariant in invariants:
        if not invariant():
            raise AssertionError(
                "%s %s failed!"
                % (
                    which,
                    repr(
                        invariant,
                    ),
                )
            )


class Step:
    def __init__(self, name, func) -> None:
        self.name = name
        self.func = func

    def __repr__(self):
        return "<Step %s>" % self.name


class Process:
    def __init__(
        self,
        name,
        steps,
        invariants: List[Callable] = [],
        endchecks: List[Callable] = [],
    ) -> None:
        self.steps = steps
        self.index = 0
        self.name = name
        self.invariants = invariants
        self.endchecks = endchecks

    def __repr__(self) -> str:
        return "<Process %s>" % (self.name)

    def next(self) -> Step:
        if self.is_done():
            raise IndexError("shouldn't call next on a done stepper")
        ret = self.steps[self.index]
        self.index += 1
        return ret

    def end(self) -> None:
        self.index = len(self.steps)

    def goto(self, name) -> None:
        for i in range(len(self.steps)):
            if self.steps[i].name == name:
                self.index = i + 1
                return
        raise ValueError(
            "No step named %s known -- known steps %s"
            % (name, repr([x.name for x in self.steps]))
        )

    def is_done(self):
        return self.index >= len(self.steps)


class Checker:
    def __init__(
        self,
        t,
        processes: List[Process],
        endchecks: List[Callable] = [],
        invariants: List[Callable] = [],
    ) -> None:
        self.t = t
        self.processes = processes
        self.invariants = invariants
        self.endchecks = endchecks


class RecordingChooser:
    def __init__(self, ch: Chooser):
        self.ch = ch
        self.selected: List[Tuple[str, Any]] = []

    def choose(self, name: str, args: List[T]) -> T:
        ret = self.ch.choose(args)
        self.selected.append((name, ret))
        return ret

    def record(self, name: str, val: Any):
        self.selected.append((name, val))


def check_all_invariants(checker: Checker):
    check_assertions("invariants", checker.invariants)
    for p in checker.processes:
        check_assertions("invariants", p.invariants)


def wrapper(states: List[int], c: Chooser, f: Callable[[Any], Checker]):
    rc = RecordingChooser(c)
    try:
        checker = f(rc)
        check_all_invariants(checker)
        # unfair process?
        while True:
            can_step = [s for s in checker.processes if not s.is_done()]
            if not can_step:
                break
            st = rc.choose("inner_proc", can_step)
            n = st.next()
            rc.selected.append(("inner_step", "%r %r" % (st, n.name)))
            states[0] += 1
            n.func(st)
            check_all_invariants(checker)

        states[0] += 1
        check_assertions("final", checker.endchecks)
    except:
        print("states: %d" % (states[0],))
        print("queue: %d" % (len(c.executions)))
        print("choices were:")
        for name, c in rc.selected:
            print("%s: %s" % (name, c))
        raise


def run(f):
    states = [0]
    run_choices(lambda c: wrapper(states, c, f))
    print("states: %d" % (states[0],))
