from chtla import RecordingChooser, Checker, Process, Action, run

# from page 15 in TLA+ book -- should fail when amount == 6


def algo(t: RecordingChooser) -> Checker:
    people = ["alice", "bob"]
    sender = "alice"
    receiver = "bob"
    acc = {p: 5 for p in people}
    amount = t.choose("amount", list(range(0, acc[sender] + 1)))

    def outer_no_overdrafts() -> bool:
        return len([i for i in acc.values() if i >= 0]) == len(people)

    def outer_endcheck() -> bool:
        return True

    def inner(num: int, t: RecordingChooser) -> Process:
        def step_withdraw(_stepper: Process) -> None:
            t.record("withdrawing %d, new balance" % (amount,), acc[sender] - amount)
            acc[sender] -= amount

        def step_deposit(_stepper: Process) -> None:
            t.record("depositing %d, new balance " % (amount,), acc[receiver] + amount)
            acc[receiver] += amount

        return Process(
            name="wire " + str(num),
            actions=[
                Action("Withdraw", step_withdraw),
                Action("Deposit", step_deposit),
            ],
        )

    return Checker(
        t,
        processes=[inner(1, t), inner(2, t)],
        invariants=[outer_no_overdrafts],
        endchecks=[outer_endcheck],
    )


if __name__ == "__main__":
    run(algo)
