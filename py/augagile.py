# https://www.hillelwayne.com/post/augmenting-agile/

from chtla import RecordingChooser, Checker, Process, Action, run, Process
from typing import List


class State:
    def __init__(self, threads: int, _chooser: RecordingChooser) -> None:
        self.occupied = 0
        self.awake = [True for i in range(threads)]


def algo(t: RecordingChooser) -> Checker["State"]:
    BuffLen = 1
    Threads = 3
    # buffer = []
    # put_at = 0
    # get_at = 0

    # choose so there's at least one each of Getter and Putter
    Putters = t.choose("putters", list(range(1, Threads)))
    # Getters = Threads - Putters

    def is_full(state: State) -> bool:
        return state.occupied == BuffLen

    def is_empty(state: State) -> bool:
        return state.occupied == 0

    def SleepingThreads(state: State) -> List[int]:
        return [i for i in range(Threads) if not state.awake[i]]

    def notify(state: State) -> None:
        st = SleepingThreads(state)

        # Fix can be this -- better to have putter and getter notification
        # and that getters/putters only notify the opposite kind
        # for i in st:
        #     awake[i] = True
        if st:
            awaken_thread = t.choose("awaken thread", st)
            state.awake[awaken_thread] = True

    def is_runnable(threadno: int, state: State) -> bool:
        return state.awake[threadno]

    def Getter(threadno: int) -> Process:
        def step_main(stepper: Process, state: State) -> None:

            if is_empty(state):
                state.awake[threadno] = False
            else:
                notify(state)
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
        )

    def Putter(threadno: int) -> Process:
        def step_main(stepper: Process, state: State) -> None:
            if is_full(state):
                state.awake[threadno] = False
            else:
                notify(state)
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
        )

    return Checker(
        t,
        processes=(
            [Putter(i) for i in range(Putters)]
            + [Getter(i) for i in range(Putters, Threads)]
        ),
        initstate=lambda ch: State(Threads, ch),
    )


if __name__ == "__main__":
    run(algo)
