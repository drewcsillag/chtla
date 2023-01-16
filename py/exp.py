from chtla import RecordingChooser, Checker, Process, Action, LabelledAction, run
from typing import Dict

class GS:
    def __init__(self) -> None:
        self.amount = 0
    def __repr__(self) -> str:
        return '<GS @ %d - amount: %d>' % (id(self), self.amount)
    def __deepcopy__(self, _ignored) -> 'GS':
        x = GS()
        x.amount = self.amount
        return x

def endcheck(state: GS) -> bool:
    print("ENDCHECK STATE IS " + repr(state))
    return state.amount == 4

def step(
    proc: Process[GS, None],
    action: LabelledAction[GS, None],
    state: GS,
    chooser: RecordingChooser
) -> GS:
    print("FIRST")
    chooser.record("FIRST Advancing state from", state)
    print("P1 Advancing state from {}".format(state))
    state.amount += 1
    chooser.record("state before label first", state.amount)
    state = action.label("first", state, chooser)
    chooser.record("SECOND state after label first", state.amount)
    print("SECOND")
    chooser.record("Advancing state from ", state)
    print("P2 Advancing state from {}".format( state))
    state.amount += 1
    chooser.record("P2 amount is now", state)
    state = action.label("second", state, chooser)
    chooser.record("P2 after final label, state", state)
    return state

def bumpit(
    proc: Process[GS, None],
    action: LabelledAction[GS, None],
    state: GS,
    chooser: RecordingChooser
) -> GS: 
    state.amount +=1
    state = action.label("bumpit2", state, chooser)
    state.amount +=1
    return state

def algo(chooser: RecordingChooser) -> Checker[GS, None]:
    return Checker(
        chooser,
        processes=[
            Process(
                name="single",
                actions=[
                    LabelledAction("main", step)
                ],
                state = None,
                fair = True
            ),
            Process(
                name="other",
                actions = [
                    LabelledAction("bumpit", bumpit)],
                state = None,
                fair=True
            )
        ],
        invariants = [],
        endchecks=[endcheck],
        initstate = lambda ch: GS()
    )
if __name__ == "__main__":
    run(algo, order = 'DFS')