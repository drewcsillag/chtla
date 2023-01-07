from choice import Chooser
from chtla import Checker, Stepper, Step, run


def algo(t: Chooser):
    people = ["alice", "bob"]
    acc = {p: 5 for p in people}
    sender = "alice"
    receiver = "bob"
    amount = 3

    def endcheck():
        print("endcheck")
        return True

    def no_overdrafts():
        print("noover")
        return len([i for i in acc.values() if i >= 0]) == len(people)

    def withdraw():
        print("with")
        acc[sender] -= amount

    def deposit():
        print("dep")
        acc[receiver] += amount

    return Checker(
        t,
        steppers=[
            Stepper(
                [
                    Step("Withdraw", withdraw),
                    Step("Deposit", deposit),
                ]
            )
        ],
        invariants=[no_overdrafts],
        endchecks=[endcheck],
    )


if __name__ == "__main__":
    run(algo)
