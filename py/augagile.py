# https://www.hillelwayne.com/post/augmenting-agile/

from chtla import RecordingChooser, Checker, Process, Action, run, Process
from typing import List


class GlobalState:
    def __init__(self, threads: int, _chooser: RecordingChooser) -> None:
        self.occupied = 0
        self.awake = [True for i in range(threads)]


BuffLen = 1
Threads = 3


def is_full(state: GlobalState) -> bool:
    return state.occupied == BuffLen


def is_empty(state: GlobalState) -> bool:
    return state.occupied == 0


def SleepingThreads(state: GlobalState) -> List[int]:
    return [i for i in range(Threads) if not state.awake[i]]


def notify(state: GlobalState, t: RecordingChooser) -> None:
    st = SleepingThreads(state)

    # Fix can be this -- better to have putter and getter notification
    # and that getters/putters only notify the opposite kind
    # for i in st:
    #     awake[i] = True
    if st:
        awaken_thread = t.choose("awaken thread", st)
        state.awake[awaken_thread] = True


def is_runnable(threadno: int, state: GlobalState) -> bool:
    return state.awake[threadno]


def Getter(threadno: int) -> Process[GlobalState, None]:
    def step_main(
        stepper: Process[GlobalState, None],
        state: GlobalState,
        chooser: RecordingChooser,
    ) -> None:

        if is_empty(state):
            state.awake[threadno] = False
        else:
            notify(state, chooser)
            state.occupied -= 1

        stepper.goto("entry")

    return Process(
        name="Getter thread %d" % (threadno,),
        fair=True,
        actions=[
            Action(
                "entry",
                step_main,
                await_fn=lambda state: is_runnable(threadno, state),
            ),
        ],
        state=None,
    )


def Putter(threadno: int) -> Process[GlobalState, None]:
    def step_main(
        stepper: Process[GlobalState, None],
        state: GlobalState,
        chooser: RecordingChooser,
    ) -> None:
        if is_full(state):
            state.awake[threadno] = False
        else:
            notify(state, chooser)
            state.occupied += 1
        stepper.goto("entry")

    return Process(
        name="Putter thread %d" % (threadno,),
        fair=True,
        actions=[
            Action(
                "entry",
                step_main,
                await_fn=lambda state: is_runnable(threadno, state),
            ),
        ],
        state=None,
    )


def algo(t: RecordingChooser) -> Checker["GlobalState", None]:
    # choose so there's at least one each of Getter and Putter
    Putters = t.choose("putters", list(range(1, Threads)))
    # Getters = Threads - Putters

    return Checker(
        t,
        processes=(
            [Putter(i) for i in range(Putters)]
            + [Getter(i) for i in range(Putters, Threads)]
        ),
        initstate=lambda ch: GlobalState(Threads, ch),
    )


if __name__ == "__main__":
    run(algo)
