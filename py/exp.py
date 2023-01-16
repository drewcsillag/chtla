from chtla import RecordingChooser, Checker, Process, Action, LabelledAction, run
from typing import Dict


class GS:
    def __init__(self) -> None:
        self.amount = 0

    def __repr__(self) -> str:
        return "<GS @ %d - amount: %d>" % (id(self), self.amount)

    def __deepcopy__(self, _ignored) -> "GS":
        x = GS()
        x.amount = self.amount
        return x


def endcheck(state: GS) -> bool:
    print("ENDCHECK STATE IS " + repr(state))
    return state.amount == 8


def step(
    proc: Process[GS, None],
    action: LabelledAction[GS, None],
    state: GS,
    chooser: RecordingChooser,
) -> GS:
    for i in range(3):
        state = action.label("infor", state, chooser)
        chooser.record("%s Advancing state from" % (i,), state)
        state.amount += 1
    return state


def bumpit(
    proc: Process[GS, None],
    action: LabelledAction[GS, None],
    state: GS,
    chooser: RecordingChooser,
) -> GS:

    while state.amount < 8:
        chooser.record("amount is <8 advancing", state.amount)
        state.amount += 1
        state = action.label("bumpit2", state, chooser)
    chooser.record("exiting while as amount >= 8", state.amount)
    return state


def algo(chooser: RecordingChooser) -> Checker[GS, None]:
    return Checker(
        chooser,
        processes=[
            Process(
                name="single",
                actions=[LabelledAction("main", step)],
                state=None,
                fair=True,
            ),
            Process(
                name="other",
                actions=[LabelledAction("bumpit", bumpit)],
                state=None,
                fair=True,
            ),
        ],
        invariants=[],
        endchecks=[endcheck],
        initstate=lambda ch: GS(),
    )


if __name__ == "__main__":
    run(algo, order="DFS")
