from chtla import RecordingChooser, Checker, Process, Action, run
from typing import Dict

# from page about 8 in TLA+ book

people = ["alice", "bob"]

sender = "alice"
receiver = "bob"
amount = 3


def endcheck(acc: Dict[str, int]) -> bool:
    print("endcheck")
    return True


def no_overdrafts(acc: Dict[str, int]) -> bool:
    print("noover")
    return len([i for i in acc.values() if i >= 0]) == len(people)


def withdraw(
    _proc: Process[Dict[str, int], None], acc: Dict[str, int], chooser: RecordingChooser
) -> None:
    print("with")
    acc[sender] -= amount


def deposit(
    _proc: Process[Dict[str, int], None], acc: Dict[str, int], chooser: RecordingChooser
) -> None:
    print("dep")
    acc[receiver] += amount


def algo(chooser: RecordingChooser) -> Checker[Dict[str, int], None]:
    return Checker(
        chooser,
        processes=[
            Process(
                name="wire",
                actions=[
                    Action("Withdraw", withdraw),
                    Action("Deposit", deposit),
                ],
                state=None,
            )
        ],
        invariants=[no_overdrafts],
        endchecks=[endcheck],
        initstate=lambda _ch: {p: 5 for p in people},
    )


if __name__ == "__main__":
    run(algo)
