from chtla import RecordingChooser, Checker, Process, Action, run

# from page 15 in TLA+ book -- should fail when amount == 6


def algo(chooser: RecordingChooser) -> Checker:
    people = ["alice", "bob"]
    sender = "alice"
    receiver = "bob"
    amount = chooser.choose("amount", list(range(0, 6)))

    def no_overdrafts(acc) -> bool:
        return len([i for i in acc.values() if i >= 0]) == len(people)

    def outer_endcheck(acc) -> bool:
        return True

    def process(num: int) -> Process:
        def step_withdraw(_proc: Process, acc) -> None:
            chooser.record(
                "withdrawing %d, new balance" % (amount,), acc[sender] - amount
            )
            acc[sender] -= amount

        def step_deposit(_proc: Process, acc) -> None:
            chooser.record(
                "depositing %d, new balance " % (amount,), acc[receiver] + amount
            )
            acc[receiver] += amount

        return Process(
            name="wire " + str(num),
            actions=[
                Action("Withdraw", step_withdraw),
                Action("Deposit", step_deposit),
            ],
        )

    return Checker(
        chooser,
        processes=[process(1), process(2)],
        invariants=[no_overdrafts],
        endchecks=[outer_endcheck],
        initstate = lambda _ch: {p: 5 for p in people}
    )


if __name__ == "__main__":
    run(algo)
