from chtla import RecordingChooser, Checker, Process, Action, run

# from page about 8 in TLA+ book


def algo(chooser: RecordingChooser) -> Checker:
    people = ["alice", "bob"]
    
    sender = "alice"
    receiver = "bob"
    amount = 3

    def endcheck(acc) -> bool:
        print("endcheck")
        return True

    def no_overdrafts(acc) -> bool:
        print("noover")
        return len([i for i in acc.values() if i >= 0]) == len(people)

    def withdraw(_proc: Process, acc) -> None:
        print("with")
        acc[sender] -= amount

    def deposit(_proc: Process, acc) -> None:
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
        initstate = lambda _ch: {p: 5 for p in people}
    )


if __name__ == "__main__":
    run(algo)
