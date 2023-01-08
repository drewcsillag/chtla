# https://www.hillelwayne.com/post/augmenting-agile/

from chtla import RecordingChooser, Checker, Process, Action, run

algoct = 0

def algo(t: RecordingChooser):
    # global algoct
    # algoct+=1
    # if algoct %1000 == 0:
    #     print("count -> " + str(algoct))
    BuffLen = 1
    Threads = 3
    # buffer = []
    # put_at = 0
    # get_at = 0
    awake = [True for i in range(Threads)]
    occupied = 0

    # set in vars
    # have to have at least one Getter, so choose up to Threads - 1
    Putters = t.choose_index('putters', Threads-1)
    Putters += 1
    # Getters = Threads - Putters

    def is_full():
        return occupied == BuffLen

    def is_empty():
        return occupied == 0

    def SleepingThreads():
        return [i for i in range(Threads) if not awake[i]]

    def notify():
        st = SleepingThreads()
        if st:
            awaken_thread = t.choose('awaken thread', st)
            # print("Waking %d" % (awaken_thread,))
            awake[awaken_thread] = True

    def Getter(threadno):
        def step_main(stepper):
            nonlocal occupied

            # print("Getter")
            if is_empty():
                t.record("G","G is_empty true %d" % (threadno,))
                awake[threadno] = False
                # print("G awake after %d %s" % (threadno, repr(awake)))
                isadvanceable(threadno)
            else:
                # print("getter GOT")
                notify()
                occupied -= 1

            stepper.goto("entry")
            
        return Process(
            name = "Getter thread %d" % (threadno,),
            fair = True,
            actions = [
                Action("entry", step_main, 
                    await_fn = lambda: isadvanceable(threadno)),
            ]
        )

    def isadvanceable(threadno):
        # print("called")
        # if not awake[threadno]:
        #     print("thread  %d blocked" % (threadno,))
        return awake[threadno]

    def Putter(threadno):
        def step_main(stepper):
            nonlocal occupied

            # print("Putter")
            if is_full():
                t.record("P", "P Sleeping %d" % (threadno,))

                awake[threadno] = False
                # print("setting awake false")
            else:
                # print("P notify")
                notify()
                occupied += 1
            stepper.goto("entry")

        return Process(
            name = "Putter thread %d" % (threadno,),
            fair = True,
            actions = [
                Action("entry", step_main, 
                    await_fn=lambda:isadvanceable(threadno)),
            ]
        )

    procs = []
    for i in range(Putters):
        procs.append(Putter(i))

    for i in range(Putters, Threads):
        procs.append(Getter(i))

    return Checker(
        t,
        processes = procs,
    )
    

if __name__ == "__main__":
    run(algo)