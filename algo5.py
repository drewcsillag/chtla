from chtla import RecordingChooser, Checker, Process, Step, run

# from page 19 in TLA+ book -- should fail when amount == 6


def algo(t: RecordingChooser):
    people = ["alice", "bob"]
    sender = "alice"
    receiver = "bob"
    acc = {p: 5 for p in people}

    def outer_no_overdrafts():
        return len([i for i in acc.values() if i >= 0]) == len(people)

    def outer_endcheck():
        return True

    def inner(num: int, t: RecordingChooser):
        amount = t.choose("amount", list(range(0, acc[sender] + 1)))

        def step_check_balance_and_withdraw(stepper):
            if amount <= acc[sender]:
                t.record("Proc %d withdrawing %d" % (num, amount), acc[sender] - amount)
                acc[sender] -= amount
            else:
                stepper.end()

        def step_deposit(_stepper):
            t.record("Proc %d depsoitngs %d" % (num, amount), acc[receiver] + amount)
            acc[receiver] += amount

        return Process(
            name="wire " + str(num),
            steps=[
                Step("CheckBalance", step_check_balance_and_withdraw),
                Step("Deposit", step_deposit),
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