from typing import Optional, Callable, List, Any
from choice import Chooser, run_choices


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


class Stepper:
    def __init__(self, steps) -> None:
        self.steps = steps
        self.index = 0

    def next(self) -> Callable:
        if self.is_done():
            raise IndexError("shouldn't call next on a done stepper")
        ret = self.steps[self.index].func
        self.index += 1
        return ret

    def goto(self, name) -> Callable:
        for i in range(self.steps):
            if self.steps[i].name == name:
                ret = self.steps
                self.index = i + 1
                return ret
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
        steppers: List[Stepper],
        invariants: List[Callable] = [],
        endchecks: List[Callable] = [],
    ) -> None:
        self.t = t
        self.steppers = steppers
        self.invariants = invariants
        self.endchecks = endchecks


def wrapper(c: Chooser, f: Callable[[Any], Checker]):
    checker = f(c)
    check_assertions("invariant", checker.invariants)
    # unfair process
    while True:
        can_step = [s for s in checker.steppers if not s.is_done()]
        if not can_step:
            break
        st = c.choose(can_step)
        n = st.next()
        n()
        check_assertions("invariant", checker.invariants)
    check_assertions("final", checker.endchecks)


def run(f):
    run_choices(lambda c: wrapper(c, f))
