from chtla import RecordingChooser, Checker, Process, Action, run
from typing import Dict

# from page 20 in TLA+ book -- should pick up on stuttering

people = ["alice", "bob"]
sender = "alice"
receiver = "bob"


class GlobalState:
    def __init__(self, _ch: RecordingChooser) -> None:
        self.acc = {p: 5 for p in people}


class ProcessState:
    def __init__(self, amount: int):
        self.amount = amount


def no_overdrafts(state: GlobalState) -> bool:
    return len([i for i in state.acc.values() if i >= 0]) == len(people)


def endcheck(state: GlobalState) -> bool:
    return state.acc["alice"] + state.acc["bob"] == 10


def step_check_balance_and_withdraw(
    proc: Process[GlobalState, ProcessState],
    state: GlobalState,
    chooser: RecordingChooser,
) -> None:
    if proc.state.amount <= state.acc[sender]:
        chooser.record(
            "withdrawing %d" % (proc.state.amount,),
            state.acc[sender] - proc.state.amount,
        )
        state.acc[sender] -= proc.state.amount
    else:
        proc.end()
    return state


def step_deposit(
    proc: Process[GlobalState, ProcessState],
    state: GlobalState,
    chooser: RecordingChooser,
) -> None:
    chooser.record(
        "depositing %d" % (proc.state.amount,), state.acc[receiver] + proc.state.amount
    )
    state.acc[receiver] += proc.state.amount
    return state


def algo(chooser: RecordingChooser) -> Checker[GlobalState, ProcessState]:
    def process(num: int) -> Process[GlobalState, ProcessState]:
        amount = chooser.choose("amount", list(range(0, 6)))

        return Process(
            name="wire " + str(num),
            actions=[
                Action("CheckBalance", step_check_balance_and_withdraw),
                Action("Deposit", step_deposit),
            ],
            state=ProcessState(amount),
        )

    return Checker(
        chooser,
        processes=[process(1), process(2)],
        invariants=[no_overdrafts],
        endchecks=[endcheck],
        initstate=GlobalState,
    )


if __name__ == "__main__":
    run(algo)
