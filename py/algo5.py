from chtla import RecordingChooser, Checker, Process, Action, run
from typing import Dict

# from page 19 in TLA+ book -- should work
people = ["alice", "bob"]
sender = "alice"
receiver = "bob"


class PS:
    def __init__(self, amount: int, num: int) -> None:
        self.amount = amount
        self.num = num


def outer_no_overdrafts(acc: Dict[str, int]) -> bool:
    return len([i for i in acc.values() if i >= 0]) == len(people)


def outer_endcheck(_acc: Dict[str, int]) -> bool:
    return True


def step_check_balance_and_withdraw(
    proc: Process[Dict[str, int], PS], acc: Dict[str, int], chooser: RecordingChooser
) -> None:
    if proc.state.amount <= acc[sender]:
        chooser.record(
            "Proc %d withdrawing %d" % (proc.state.num, proc.state.amount),
            acc[sender] - proc.state.amount,
        )
        acc[sender] -= proc.state.amount
    else:
        proc.end()  # stop the process
    return acc


def step_deposit(
    proc: Process[Dict[str, int], PS], acc: Dict[str, int], chooser: RecordingChooser
) -> None:
    chooser.record(
        "Proc %d depositing %d" % (proc.state.num, proc.state.amount),
        acc[receiver] + proc.state.amount,
    )
    acc[receiver] += proc.state.amount
    return acc


def process(num: int, chooser: RecordingChooser) -> Process[Dict[str, int], PS]:
    return Process(
        name="wire " + str(num),
        actions=[
            Action("CheckBalance", step_check_balance_and_withdraw),
            Action("Deposit", step_deposit),
        ],
        state=PS(chooser.choose("amount", list(range(0, 6))), num),
    )


def algo(chooser: RecordingChooser) -> Checker[Dict[str, int], PS]:
    return Checker(
        chooser,
        processes=[process(1, chooser), process(2, chooser)],
        invariants=[outer_no_overdrafts],
        endchecks=[outer_endcheck],
        initstate=lambda _ch: {p: 5 for p in people},
    )


if __name__ == "__main__":
    run(algo, order="DFS")
