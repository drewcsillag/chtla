from chtla import RecordingChooser, Checker, Process, Action, LabelledAction, run
from typing import Any, List


class GS:
    def __init__(self) -> None:
        self.amount = 0
        self.hits :List[str] = []

    def __repr__(self) -> str:
        return "<GS @ %d - amount: %d hits:%r>" % (id(self), self.amount, self.hits)


def endcheck(state: GS) -> bool:
    r = (state.amount == 6)
    # if str(state.hits) == "['step2:info0', 'step1:info0', 'step1:info1']":
    #     return False

    return r

def step(
    proc: Process[GS, None],
    action: LabelledAction[GS, None],
    state: GS,
    chooser: RecordingChooser,
) -> GS:
    state.hits.append(proc.name + ":info" + str(0))
    state.amount += 1
    ## constrain it so step1 and step2 do not proceed until they've both
    ## gotten here
    state = action.do_await("info", lambda s: s.amount >= 2, state, chooser)

    state.hits.append(proc.name + ":info" + str(1))
    state.amount += 1
    state = action.label("info", state, chooser)

    state.hits.append(proc.name + ":info" + str(2))
    state.amount += 1

    return state

def docheck(
    proc: Process[GS, None],
    state: GS,
    chooser: RecordingChooser,
) -> GS:
    print("XXX:" + repr(state.hits))
    return state

def algo(chooser: RecordingChooser) -> Checker[GS, None]:
    return Checker(
        chooser,
        processes=[
            Process(
                name="step1",
                actions=[LabelledAction("main", step)],
                state=None,
                fair=True,
            ),
            Process(
                name="step2",
                actions=[LabelledAction("main", step)],
                state=None,
                fair=True,
            ),
            Process(
                name = "checkthing",
                actions = [
                    Action(
                        "check", 
                        docheck, 
                        lambda state: state.amount == 6, 
                        fair = True)
                ],
                state=None
            )
        ],
        invariants=[],
        endchecks=[endcheck],
        initstate=lambda ch: GS(),
    )


if __name__ == "__main__":
    run(algo, order="DFS")
