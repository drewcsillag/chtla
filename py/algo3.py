from chtla import RecordingChooser, Checker, Process, Action, run
from typing import Dict

# from page 15 in TLA+ book -- should fail when amount == 6


people = ["alice", "bob"]
sender = "alice"
receiver = "bob"


def no_overdrafts(acc: Dict[str, int]) -> bool:
    return len([i for i in acc.values() if i >= 0]) == len(people)


def outer_endcheck(acc: Dict[str, int]) -> bool:
    return True


def step_withdraw(
    proc: Process[Dict[str, int], int], acc: Dict[str, int], chooser: RecordingChooser
) -> None:
    chooser.record(
        "withdrawing %d, new balance" % (proc.state,), acc[sender] - proc.state
    )
    acc[sender] -= proc.state


def step_deposit(
    proc: Process[Dict[str, int], int], acc: Dict[str, int], chooser: RecordingChooser
) -> None:
    chooser.record(
        "depositing %d, new balance " % (proc.state,), acc[receiver] + proc.state
    )
    acc[receiver] += proc.state


def process(num: int, chooser: RecordingChooser) -> Process[Dict[str, int], int]:
    return Process(
        name="wire " + str(num),
        actions=[
            Action("Withdraw", step_withdraw),
            Action("Deposit", step_deposit),
        ],
        state=chooser.choose("amount", list(range(0, 6))),
    )


def algo(chooser: RecordingChooser) -> Checker[Dict[str, int], int]:

    return Checker(
        chooser,
        processes=[process(1, chooser), process(2, chooser)],
        invariants=[no_overdrafts],
        endchecks=[outer_endcheck],
        initstate=lambda _ch: {p: 5 for p in people},
    )


if __name__ == "__main__":
    run(algo)
