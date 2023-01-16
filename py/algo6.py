from chtla import RecordingChooser, Checker, Process, Action, run
from typing import Dict

# from page 20 in TLA+ book -- should pick up on stuttering


def algo(chooser: RecordingChooser) -> Checker[Dict[str, int]]:
    people = ["alice", "bob"]
    sender = "alice"
    receiver = "bob"

    def no_overdrafts(acc: Dict[str, int]) -> bool:
        return len([i for i in acc.values() if i >= 0]) == len(people)

    def endcheck(acc: Dict[str, int]) -> bool:
        return acc["alice"] + acc["bob"] == 10

    def process(num: int) -> Process:
        amount = chooser.choose("amount", list(range(0, 6)))

        def step_check_balance_and_withdraw(proc: Process, acc: Dict[str, int]) -> None:
            if amount <= acc[sender]:
                chooser.record("withdrawing %d" % (amount,), acc[sender] - amount)
                acc[sender] -= amount
            else:
                proc.end()

        def step_deposit(_proc: Process, acc: Dict[str, int]) -> None:
            chooser.record("depositing %d" % (amount,), acc[receiver] + amount)
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
        invariants=[no_overdrafts],
        endchecks=[endcheck],
        initstate=lambda _ch: {p: 5 for p in people},
    )


if __name__ == "__main__":
    run(algo)
