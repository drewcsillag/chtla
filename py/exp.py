from chtla import RecordingChooser, Checker, Process, Action, LabelledAction, run
from typing import Any, List


class GS:
    def __init__(self) -> None:
        self.amount = 0
        self.hits :List[str] = []

    def __repr__(self) -> str:
        return "<GS @ %d - amount: %d>" % (id(self), self.amount)


def endcheck(state: GS) -> bool:
    r = (state.amount == 4)
    if str(state.hits) == "['step2:info0', 'step2:info1', 'step1:info0', 'step1:info1']":
        return False

    return r


def step(
    proc: Process[GS, None],
    action: LabelledAction[GS, None],
    state: GS,
    chooser: RecordingChooser,
) -> GS:
    for i in range(2):
        state = action.label("info", state, chooser)
        state.hits += [proc.name + ":info" + str(i)]
        sel = 1
        state.amount += sel
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
                        lambda state: state.amount == 4, 
                        fair =True)
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
