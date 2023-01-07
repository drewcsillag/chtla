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


class Action:
    def __init__(self, name, func) -> None:
        self.name = name
        self.func = func

    def __repr__(self):
        return "<Action %s>" % self.name


class Process:
    def __init__(
        self,
        name,
        actions,
        invariants: List[Callable] = [],
        endchecks: List[Callable] = [],
    ) -> None:
        self.actions = actions
        self.index = 0
        self.name = name
        self.invariants = invariants
        self.endchecks = endchecks

    def __repr__(self) -> str:
        return "<Process %s>" % (self.name)

    def next(self) -> Action:
        if self.is_done():
            raise IndexError("shouldn't call next on a done Process")
        ret = self.actions[self.index]
        self.index += 1
        return ret

    def end(self) -> None:
        self.index = len(self.actions)

    def goto(self, name) -> None:
        for i in range(len(self.actions)):
            if self.actions[i].name == name:
                self.index = i + 1
                return
        raise ValueError(
            "No action named %s known -- known actions %s"
            % (name, repr([x.name for x in self.actions]))
        )

    def is_done(self):
        return self.index >= len(self.actions)


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
        self.proc = None

    def choose(self, name: str, args: List[T]) -> T:
        ret = self.ch.choose(args)
        self.record(name, ret)
        return ret

    def record(self, name: str, val: Any):
        self.selected.append(("%-20r %s" % (self.proc, name), val))

    def set_proc(self, proc: Process):
        self.proc = proc


def check_all_invariants(checker: Checker):
    check_assertions("invariants", checker.invariants)
    for p in checker.processes:
        check_assertions("invariants", p.invariants)


def wrapper(states: List[int], c: Chooser, f: Callable[[Any], Checker]):
    rc = RecordingChooser(c)
    try:
        checker = f(rc)
        check_all_invariants(checker)
        # unfair process? Yes (because we kill processes)
        while True:
            live_processes = [p for p in checker.processes if not p.is_done()]
            if not live_processes:
                break

            rc.set_proc("scheduler")
            proc = rc.choose("scheduling_proc", live_processes)
            
            if rc.choose("kill proc %r?" % (proc,), [False, True]):
                rc.set_proc(proc)
                rc.record("process died", True)
                proc.end()
            else:
                rc.set_proc(proc)

                n = proc.next()
                rc.record("inner_step", n.name)

                states[0] += 1
                n.func(proc)

            rc.set_proc(None)

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
