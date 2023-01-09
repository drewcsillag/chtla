from chtla import RecordingChooser, Checker, Process, Action, run

# from page about 8 in TLA+ book


def algo(chooser: RecordingChooser) -> Checker:
    people = ["alice", "bob"]
    acc = {p: 5 for p in people}
    sender = "alice"
    receiver = "bob"
    amount = 3

    def endcheck() -> bool:
        print("endcheck")
        return True

    def no_overdrafts() -> bool:
        print("noover")
        return len([i for i in acc.values() if i >= 0]) == len(people)

    def withdraw(_proc: Process) -> None:
        print("with")
        acc[sender] -= amount

    def deposit(_proc: Process) -> None:
        print("dep")
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
    )


if __name__ == "__main__":
    run(algo)
