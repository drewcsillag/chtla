from chtla import RecordingChooser, Checker, Process, Action, run

# from page 19 in TLA+ book -- should work


def algo(chooser: RecordingChooser) -> Checker:
    people = ["alice", "bob"]
    sender = "alice"
    receiver = "bob"
    acc = {p: 5 for p in people}

    def outer_no_overdrafts() -> bool:
        return len([i for i in acc.values() if i >= 0]) == len(people)

    def outer_endcheck() -> bool:
        return True

    def process(num: int) -> Process:
        amount = chooser.choose("amount", list(range(0, acc[sender] + 1)))

        def step_check_balance_and_withdraw(proc: Process) -> None:
            if amount <= acc[sender]:
                chooser.record(
                    "Proc %d withdrawing %d" % (num, amount), acc[sender] - amount
                )
                acc[sender] -= amount
            else:
                proc.end()  # stop the process

        def step_deposit(_proc: Process) -> None:
            chooser.record(
                "Proc %d depositing %d" % (num, amount), acc[receiver] + amount
            )
            acc[receiver] += amount

        return Process(
            name="wire " + str(num),
            actions=[
                Action("CheckBalance", step_check_balance_and_withdraw),
                Action("Deposit", step_deposit),
            ],
        )

    return Checker(
        chooser,
        processes=[process(1), process(2)],
        invariants=[outer_no_overdrafts],
        endchecks=[outer_endcheck],
    )


if __name__ == "__main__":
    run(algo)
