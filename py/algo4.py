from chtla import RecordingChooser, Checker, Process, Action, run

# from page 16 in TLA+ book -- should fail when amount == 6


def algo(chooser: RecordingChooser) -> Checker:
    people = ["alice", "bob"]
    sender = "alice"
    receiver = "bob"
    acc = {p: 5 for p in people}

    def no_overdrafts() -> bool:
        return len([i for i in acc.values() if i >= 0]) == len(people)

    def endcheck() -> bool:
        return True

    def process(num: int) -> Process:
        amount = chooser.choose("amount " + str(num), list(range(0, acc[sender] + 1)))

        def step_check_balance(proc: Process) -> None:
            if amount <= acc[sender]:
                pass
            else:
                proc.end()

        def step_withdraw(_proc: Process) -> None:
            chooser.record(
                "withdrawing %d, new balance" % (amount,), acc[sender] - amount
            )
            acc[sender] -= amount

        def step_deposit(_proc: Process) -> None:
            chooser.record(
                "depositing %d, new balance " % (amount,), acc[receiver] + amount
            )
            acc[receiver] += amount

        return Process(
            name="wire " + str(num),
            actions=[
                Action("CheckBalance", step_check_balance),
                Action("Withdraw", step_withdraw),
                Action("Deposit", step_deposit),
            ],
        )

    return Checker(
        chooser,
        processes=[process(1), process(2)],
        invariants=[no_overdrafts],
        endchecks=[endcheck],
    )


if __name__ == "__main__":
    run(algo)
