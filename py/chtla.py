from typing import Optional, Callable, List, Any, TypeVar, Tuple
from choice import Chooser, run_choices, BfsException, BFS

T = TypeVar("T")


def check_assertions(which: str, invariants: List[Callable[[], bool]]) -> None:
    """Given the list of checks in invariants, execute them, using the which param
    to mark it when it fails"""
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
    def __init__(
        self,
        name: str,
        func: Callable[["Process"], None],
        await_fn: Callable[[], bool] = lambda: True,
        fair: bool = False,
    ) -> None:
        self.name = name
        self.func = func
        self.fair = fair
        self.await_fn = await_fn

    def __repr__(self) -> str:
        return "<Action %s>" % self.name

    def advanceable(self) -> bool:
        """Returns true if the Action can be executed, false if it's blocked"""
        return self.await_fn()


class Process:
    """A representation of a Process in the model checker"""

    def __init__(
        self,
        name: str,
        actions: List[Action],
        fair: bool = False,
    ) -> None:
        self.actions = actions
        self.index = 0
        self.name = name
        self.fair = fair

    def __repr__(self) -> str:
        return "<Process %s>" % (self.name)

    def peek(self) -> Action:
        """Return the next Action that would run"""
        if self.is_done():
            raise IndexError("shouldn't call peek on a done Process")
        return self.actions[self.index]

    def next(self) -> Action:
        """Return the next Action and advance to the next"""
        if self.is_done():
            raise IndexError("shouldn't call next on a done Process")
        ret = self.actions[self.index]
        self.index += 1
        return ret

    def end(self) -> None:
        """stop the process so it effectively is dead"""
        self.index = len(self.actions)

    def goto(self, name: str) -> None:
        """Go to a named action in the list of Actions"""
        for i in range(len(self.actions)):
            if self.actions[i].name == name:
                self.index = i
                return
        raise ValueError(
            "No action named %s known -- known actions %s"
            % (name, repr([x.name for x in self.actions]))
        )

    def is_done(self) -> bool:
        """Returns true of the process is done/dead"""
        return self.index >= len(self.actions)


class RecordingChooser:
    def __init__(self, ch: Chooser):
        self.ch = ch
        self.selected: List[Tuple[str, Any]] = []
        self.proc: str = "init"

    def choose_index(self, name: str, n: int) -> int:
        """Choose a value between 0 and n-1, uses the name for debugging"""
        ret = self.ch.choose_index(n)
        self.record(name, ret)
        return ret

    def choose(self, name: str, args: List[T]) -> T:
        """Choose from a list of alternatives, uses the name for debugging"""
        ret = self.ch.choose(args)
        self.selected.append(("C %-20s %s" % (self.proc, name), ret))
        return ret

    def record(self, name: str, val: Any) -> None:
        """Records an event that will be reported if the model check fails"""
        self.selected.append(("I %-20s %s" % (self.proc, name), val))

    def set_proc(self, proc: str) -> None:
        self.proc = proc


class Checker:
    """Representation of the model checker"""

    def __init__(
        self,
        chooser: RecordingChooser,  # the chooser
        processes: List[Process],  # the process list
        endchecks: List[Callable[[], bool]] = [],  # end checks []<>
        invariants: List[Callable[[], bool]] = [],  # invariants <>
    ) -> None:
        self.chooser = chooser
        self.processes = processes
        self.invariants = invariants
        self.endchecks = endchecks


def check_all_invariants(checker: Checker) -> None:
    check_assertions("invariants", checker.invariants)


radius = 0


def wrapper(
    states: List[int], c: Chooser, f: Callable[[RecordingChooser], Checker]
) -> None:
    rc = RecordingChooser(c)
    global radius
    if rc.ch.executions:
        if len(rc.ch.executions[0]) > radius:
            radius = len(rc.ch.executions[0])
            print("Radius -> " + str(radius))
            print("   R2 ->  " + str(len(rc.ch.executions[-1])))
            print("   Queue -> " + str(len(rc.ch.executions)))
    try:
        checker = f(rc)
        check_all_invariants(checker)
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
                    rc.set_proc(proc.name)
                    rc.record("process died", True)
                    proc.end()
                    killed = True

            if not killed:
                rc.set_proc(proc.name)
                rc.record("inner_step", next_action.name)

                states[0] += 1
                next_action.func(proc)

            rc.set_proc("none")

            check_all_invariants(checker)

        states[0] += 1
        check_assertions("final", checker.endchecks)
    except BfsException:
        raise
    except:
        print("states: %d" % (states[0],))
        print("queue: %d" % (len(c.executions)))
        print("len(queue[-1]) " + str(len(c.executions[-1])))
        print("diameter len(queue[0]) " + str(len(c.executions[0])))
        print("choices were:")
        for name, c in rc.selected:
            print("%s: %s" % (name, c))
        raise


def run(f: Callable[[RecordingChooser], Checker], order: str = BFS) -> None:
    states = [0]
    run_choices(lambda c: wrapper(states, c, f), order=order)
    print("states: %d" % (states[0],))
