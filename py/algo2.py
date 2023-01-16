from chtla import RecordingChooser, Checker, Process, Action, run
from typing import Dict
# from page 12 in TLA+ book -- should fail when amount == 6


def algo(chooser: RecordingChooser) -> Checker:
    people = ["alice", "bob"]
    sender = "alice"
    receiver = "bob"
    amount = chooser.choose("amount", list(range(1, 7)))

    def endcheck(acc) -> bool:
        return True

    def no_overdrafts(acc) -> bool:
        return len([i for i in acc.values() if i >= 0]) == len(people)

    def withdraw(_proc: Process, acc: Dict[str, int]) -> None:
        acc[sender] -= amount

    def deposit(_proc: Process, acc: Dict[str, int]) -> None:
        acc[receiver] += amount

    return Checker(
        chooser,
        processes=[
            Process(
                name="wire",
                actions=[
                    Action("Withdraw", withdraw),
                    Action("Deposit", deposit),
                ],
            )
        ],
        invariants=[no_overdrafts],
        endchecks=[endcheck],
        initstate = lambda _ch: {p: 5 for p in people}
    )


if __name__ == "__main__":
    run(algo)
