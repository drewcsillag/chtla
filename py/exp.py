from chtla import RecordingChooser, Checker, Process, Action, LabelledAction, run
from typing import Any


class GS:
    def __init__(self) -> None:
        self.amount = 0

    def __repr__(self) -> str:
        return "<GS @ %d - amount: %d>" % (id(self), self.amount)

    def __deepcopy__(self, _ignored:Any) -> "GS":
        x = GS()
        x.amount = self.amount
        return x


def endcheck(state: GS) -> bool:
    r = state.amount <= 4 and state.amount > 2
    print("ENDCHECK STATE IS " + repr(state) + " " + str(r))
    return r


def step(
    proc: Process[GS, None],
    action: LabelledAction[GS, None],
    state: GS,
    chooser: RecordingChooser,
) -> GS:
    for i in range(3):
        state = action.label("infor", state, chooser)
        chooser.record("%s Advancing state from" % (i,), state)
        sel = chooser.choose("picking 1 or 2", [2,1])
        state.amount += sel
        chooser.record("selection", sel)
    return state


def advance_and_label(state: GS, action: LabelledAction[GS, None], chooser: RecordingChooser) -> GS:
    state.amount += 1
    state = action.label("bumpit2", state, chooser)
    return state

def bumpit(
    proc: Process[GS, None],
    action: LabelledAction[GS, None],
    state: GS,
    chooser: RecordingChooser,
) -> GS:

    while state.amount < 4:
        chooser.record("amount is <8 advancing", state.amount)
        state = advance_and_label(state, action, chooser)
        
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
            # Process(
            #     name="other",
            #     actions=[LabelledAction("bumpit", bumpit)],
            #     state=None,
            #     fair=True,
            # ),
        ],
        invariants=[],
        endchecks=[endcheck],
        initstate=lambda ch: GS(),
    )


if __name__ == "__main__":
    run(algo, order="DFS")
