from typing import Optional, Callable, List, Any, TypeVar, Tuple
from choice import Chooser, run_choices, BfsException, BFS

T = TypeVar("T")


def check_assertions(which, invariants) -> None:
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
    def __init__(self, name, func, await_fn=lambda: True, fair=False) -> None:
        self.name = name
        self.func = func
        self.fair = fair
        self.await_fn = await_fn

    def __repr__(self) -> str:
        return "<Action %s>" % self.name

    def advanceable(self) -> bool:
        return self.await_fn()


class Process:
    def __init__(
        self,
        name,
        actions,
        invariants: List[Callable] = [],
        endchecks: List[Callable] = [],
        fair=False,
    ) -> None:
        self.actions = actions
        self.index = 0
        self.name = name
        self.invariants = invariants
        self.endchecks = endchecks
        self.fair = fair

    def __repr__(self) -> str:
        return "<Process %s>" % (self.name)

    def peek(self) -> Action:
        if self.is_done():
            raise IndexError("shouldn't call peek on a done Process")
        return self.actions[self.index]

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
                self.index = i
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
        self.proc: Optional[Any] = None

    def choose_index(self, name: str, n: int) -> int:
        ret = self.ch.choose_index(n)
        self.record(name, ret)
        return ret

    def choose(self, name: str, args: List[T]) -> T:
        ret = self.ch.choose(args)
        self.record(name, ret)
        return ret

    def record(self, name: str, val: Any):
        self.selected.append(("%-20r %s" % (self.proc, name), val))

    def set_proc(self, proc: Any):
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

            # which processes can make progress?
            advanceable_processes = [
                p for p in live_processes if p.peek().advanceable()
            ]

            if not advanceable_processes:
                raise AssertionError("Deadlock detected, no live processes can proceed")

            rc.set_proc("scheduler")
            proc = rc.choose("scheduling_proc", advanceable_processes)

            next_action = proc.next()

            killed = False
            if not proc.fair and not next_action.fair:
                kill_proc = rc.choose("kill proc %r?" % (proc,), [False, True])
                if kill_proc:
                    rc.set_proc(proc)
                    rc.record("process died", True)
                    proc.end()
                    killed = True

            if not killed:
                rc.set_proc(proc)
                rc.record("inner_step", next_action.name)

                states[0] += 1
                next_action.func(proc)

            rc.set_proc(None)

            check_all_invariants(checker)

        states[0] += 1
        check_assertions("final", checker.endchecks)
    except BfsException:
        raise
    except:
        print("states: %d" % (states[0],))
        print("queue: %d" % (len(c.executions)))
        print("choices were:")
        for name, c in rc.selected:
            print("%s: %s" % (name, c))
        raise


def run(f, order=BFS):
    states = [0]
    run_choices(lambda c: wrapper(states, c, f), order=order)
    print("states: %d" % (states[0],))
