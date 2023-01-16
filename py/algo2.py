from chtla import RecordingChooser, Checker, Process, Action, run
from typing import Dict

# from page 12 in TLA+ book -- should fail when amount == 6
people = ["alice", "bob"]
sender = "alice"
receiver = "bob"


def endcheck(acc: Dict[str, int]) -> bool:
    return True


def no_overdrafts(acc: Dict[str, int]) -> bool:
    return len([i for i in acc.values() if i >= 0]) == len(people)


def withdraw(
    proc: Process[Dict[str, int], int], acc: Dict[str, int], ch: RecordingChooser
) -> None:
    acc[sender] -= proc.state


def deposit(
    proc: Process[Dict[str, int], int], acc: Dict[str, int], ch: RecordingChooser
) -> None:
    acc[receiver] += proc.state


def algo(chooser: RecordingChooser) -> Checker[Dict[str, int], int]:
    return Checker(
        chooser,
        processes=[
            Process(
                name="wire",
                actions=[
                    Action("Withdraw", withdraw),
                    Action("Deposit", deposit),
                ],
                state=chooser.choose("amount", list(range(1, 7))),
            )
        ],
        invariants=[no_overdrafts],
        endchecks=[endcheck],
        initstate=lambda _ch: {p: 5 for p in people},
    )


if __name__ == "__main__":
    run(algo)
