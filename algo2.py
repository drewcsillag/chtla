from chtla import RecordingChooser, Checker, Process, Action, run

# from page 12 in TLA+ book -- should fail when amount == 6


def algo(t: RecordingChooser) -> Checker:
    people = ["alice", "bob"]
    acc = {p: 5 for p in people}
    sender = "alice"
    receiver = "bob"
    amount = t.choose("amount", list(range(1, 7)))

    def endcheck() -> bool:
        return True

    def no_overdrafts() -> bool:
        return len([i for i in acc.values() if i >= 0]) == len(people)

    def withdraw(_stepper: Process) -> None:
        acc[sender] -= amount

    def deposit(_stepper: Process) -> None:
        acc[receiver] += amount

    return Checker(
        t,
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
    )


if __name__ == "__main__":
    run(algo)
