from typing import Optional, Callable, List, Any, TypeVar, Tuple, Generic, cast
from choice import Chooser, run_choices, BfsException, BFS
import copy

T = TypeVar("T")
GS = TypeVar("GS")  # Global state
PS = TypeVar("PS")  # Process State


def check_assertions(
    which: str, invariants: List[Callable[[GS], bool]], state: GS
) -> None:
    """Given the list of checks in invariants, execute them, using the which param
    to mark it when it fails"""
    for invariant in invariants:
        if not invariant(state):
            raise AssertionError(
                "%s %s failed!"
                % (
                    which,
                    repr(
                        invariant,
                    ),
                )
            )


class BaseAction(Generic[GS, PS]):
    def __init__(self, name: str, fair: bool) -> None:
        self.name = name
        self.fair = fair

    def __repr__(self) -> str:
        raise NotImplementedError()

    def advanceable(self, state: GS) -> bool:
        raise NotImplementedError()

    def run(
        self, process: "Process[GS,PS]", state: GS, chooser: "RecordingChooser"
    ) -> GS:
        raise NotImplementedError()


class Action(BaseAction[GS, PS], Generic[GS, PS]):
    def __init__(
        self,
        name: str,
        func: Callable[["Process[GS,PS]", GS, "RecordingChooser"], GS],
        await_fn: Callable[[GS], bool] = lambda _s: True,
        fair: bool = False,
    ) -> None:
        super().__init__(name, fair)
        self.func = func
        self.await_fn = await_fn

    def __repr__(self) -> str:
        return "<Action %s>" % self.name

    def advanceable(self, state: GS) -> bool:
        """Returns true if the Action can be executed, false if it's blocked"""
        return self.await_fn(state)

    def run(
        self, process: "Process[GS,PS]", state: GS, chooser: "RecordingChooser"
    ) -> GS:
        return self.func(process, state, chooser)


class LabelException(Exception, Generic[GS]):
    def __init__(self, state: GS) -> None:
        self.state = state

    
class LabelledAction(BaseAction[GS, PS]):
    def __init__(
        self,
        name: str,
        func: Callable[
            ["Process[GS, PS]", "LabelledAction[GS, PS]", GS, "RecordingChooser"], GS
        ],
        fair: bool = False,
    ) -> None:
        super().__init__(name, fair)
        self.current_await_fn: Callable[[GS], bool] = lambda _s: True
        self.func = func

        self.done = False
        self.ct = 0
        self.firstrun = True # Should be able to get rid of this
        self.state_checkpoints: List[GS] = []
        self.checkpoint_index = -1
        self.choices_to_make: List[int] = []

    def __repr__(self) -> str:
        return "<LabelledAction %s>" % self.name

    def advanceable(self, state: GS) -> bool:
        """Returns true if the Action can be executed, false if it's blocked"""
        return self.current_await_fn(state)

    def get_done_and_reset(self) -> bool:
        r = self.done
        if r:
            self.done = False
            self.state_checkpoints = []
            self.checkpoint_index = -1
            self.choices_to_make = []
        return r

    def run(
        self, process: "Process[GS, PS]", state: GS, chooser: "RecordingChooser"
    ) -> GS:
        print("LA - RUN -- " + str(self.ct))
        self.ct += 1
        self.state_checkpoints.append(copy.deepcopy(state))
        cpc = CheckPointChooser(chooser, self.choices_to_make)
        state_to_run_with = self.state_checkpoints[0]
        self.checkpoint_index = 1
        
        try:
            self.func(process, self, state_to_run_with, chooser)
        except LabelException as le:
            self.choices_to_make += cpc.replay_new
            ret = le.state

        else:
            chooser.record("labelled action completed", self)
            self.done = True
            ret = state_to_run_with

        for name, c in chooser.selected:
            print("%s: %s" % (name, c))
        print("LA - /RUN\n")
        return ret


    def label(self, name: str, state: GS, chooser:"RecordingChooser") -> GS:
        chooser.record("Label:", name)

        # if still replaying...
        if self.checkpoint_index < len(self.state_checkpoints):
            chooser.record("at label, still replaying", name)
            ret = self.state_checkpoints[self.checkpoint_index]
            self.checkpoint_index += 1
            return ret

        chooser.record("REPLAY TO THIS POINT IS COMPLETE, scheduling", name)
        print("REPLAY TO THIS POINT IS DONE, scheduling after:" + name)
        raise LabelException(state)

    def set_current_await(self, await_fn: Callable[[GS], bool]) -> None:
        self.await_fn = await_fn


class Process(Generic[GS, PS]):
    """A representation of a Process in the model checker"""

    def __init__(
        self,
        name: str,
        state: PS,
        actions: List[BaseAction[GS, PS]],
        fair: bool = False,
    ) -> None:
        self.actions = actions
        self.index = 0
        self.name = name
        self.fair = fair
        self.state = state

    def __repr__(self) -> str:
        return "<Process @%d - %s>" % (id(self), self.name)

    def peek(self) -> BaseAction[GS, PS]:
        """Return the next Action that would run"""
        if self.is_done():
            raise IndexError("shouldn't call peek on a done Process")
        return self.actions[self.index]

    def next(self) -> BaseAction[GS, PS]:
        """Return the next Action and advance to the next"""
        if self.is_done():
            raise IndexError("shouldn't call next on a done Process")
        ret = self.actions[self.index]

        # can't find a better way to do this that keeps mypy happy
        if ret.__class__.__name__ == LabelledAction.__name__:
            if cast(LabelledAction[GS, PS], ret).get_done_and_reset():
                self.index += 1
                return self.next()
            else:
                return ret  # don't advance the counter
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
        if self.index >= len(self.actions):
            return True
        action = self.actions[self.index]
        if action.__class__.__name__ == LabelledAction.__name__:
            if cast(LabelledAction[GS, PS], action).get_done_and_reset():
                self.index += 1
                if self.index >= len(self.actions):
                    return True

        return False


class RecordingChooser:
    def __init__(self, ch: Chooser):
        self.ch = ch
        self.selected: List[Tuple[str, Any]] = []
        self.proc: str = "init"

    def choose_index(self, name: str, n: int) -> int:
        """Choose a value between 0 and n-1, uses the name for debugging"""
        ret = self.ch.choose_index(n)
        self.record(name + ": chose index", ret)
        return ret

    def choose(self, name: str, args: List[T]) -> T:
        """Choose from a list of alternatives, uses the name for debugging"""
        try:
            index = self.choose_index(name, len(args))
            ret = args[index]
        except IndexError:
            print("trying index %d of %r" % (index, args))
            raise
        self.selected.append(("C[%d] %-20s %s" % (len(args), self.proc, name), ret))
        return ret

    def record(self, name: str, val: Any) -> None:
        """Records an event that will be reported if the model check fails"""
        self.selected.append(("I %-20s %s" % (self.proc, name), val))

    def set_proc(self, proc: str) -> None:
        self.proc = proc

class CheckPointChooser(RecordingChooser):
    def __init__(self, rc: RecordingChooser, choices:List[int]) -> None:
        super().__init__(rc.ch)
        self.is_replaying = True
        self.replay_choices: List[int] = choices
        self.replay_index = 0
        self.replay_new: List[int] = []
        self.rc = rc

    def choose_index(self, name: str, n: int) -> int:
        if self.replay_index < len(self.replay_choices):
            ret = self.replay_choices[self.replay_index]
            self.replay_index += 1
        else:
            ret = self.rc.choose_index(name, n)
            self.replay_new.append(ret)
        return ret
        
class Checker(Generic[GS, PS]):
    """Representation of the model checker"""

    def __init__(
        self,
        chooser: RecordingChooser,  # the chooser
        processes: List[Process[GS, PS]],  # the process list
        initstate: Callable[[RecordingChooser], GS],
        endchecks: List[Callable[[GS], bool]] = [],  # end checks []<>
        invariants: List[Callable[[GS], bool]] = [],  # invariants <>
    ) -> None:
        self.chooser = chooser
        self.processes = processes
        self.invariants = invariants
        self.endchecks = endchecks
        self.initstate = initstate


def check_all_invariants(checker: Checker[GS, PS], state: GS) -> None:
    check_assertions("invariants", checker.invariants, state)


radius = 0


def wrapper(
    states: List[int], c: Chooser, f: Callable[[RecordingChooser], Checker[GS, PS]]
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
        state = checker.initstate(rc)
        check_all_invariants(checker, state)
        while True:
            live_processes = [p for p in checker.processes if not p.is_done()]
            if not live_processes:
                break

            # which processes can make progress?
            advanceable_processes = [
                p for p in live_processes if p.peek().advanceable(state)
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
                state = next_action.run(proc, state, rc)

            rc.set_proc("none")

            check_all_invariants(checker, state)

        states[0] += 1
        check_assertions("final", checker.endchecks, state)
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


def run(f: Callable[[RecordingChooser], Checker[GS, PS]], order: str = BFS) -> None:
    states = [0]
    run_choices(lambda c: wrapper(states, c, f), order=order)
    print("states: %d" % (states[0],))
