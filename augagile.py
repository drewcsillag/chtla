# https://www.hillelwayne.com/post/augmenting-agile/

from chtla import RecordingChooser, Checker, Process, Action, run


def algo(t: RecordingChooser):
    BuffLen = 1
    Threads = 5
    # buffer = []
    # put_at = 0
    # get_at = 0
    awake = [True for i in range(Threads)]
    occupied = 0
    # choose so there's at least one each of Getter and Putter
    Putters = t.choose("putters", list(range(1, Threads)))
    # Getters = Threads - Putters

    def is_full():
        return occupied == BuffLen

    def is_empty():
        return occupied == 0

    def SleepingThreads():
        return [i for i in range(Threads) if not awake[i]]

    def notify():
        st = SleepingThreads()

        # Fix can be this -- better to have putter and getter notification
        # and that getters/putters only notify the opposite kind
        # for i in st:
        #     awake[i] = True
        if st:
            awaken_thread = t.choose("awaken thread", st)
            awake[awaken_thread] = True

    def is_runnable(threadno):
        return awake[threadno]

    def Getter(threadno):
        def step_main(stepper):
            nonlocal occupied

            if is_empty():
                awake[threadno] = False
            else:
                notify()
                occupied -= 1

            stepper.goto("entry")

        return Process(
            name="Getter thread %d" % (threadno,),
            fair=True,
            actions=[
                Action("entry", step_main, await_fn=lambda: is_runnable(threadno)),
            ],
        )

    def Putter(threadno):
        def step_main(stepper):
            nonlocal occupied

            if is_full():
                awake[threadno] = False
            else:
                notify()
                occupied += 1
            stepper.goto("entry")

        return Process(
            name="Putter thread %d" % (threadno,),
            fair=True,
            actions=[
                Action("entry", step_main, await_fn=lambda: is_runnable(threadno)),
            ],
        )

    return Checker(
        t,
        processes= (
            [Putter(i) for i in range(Putters)] +
            [Getter(i) for i in range(Putters, Threads)]
        ),
    )


if __name__ == "__main__":
    run(algo)
