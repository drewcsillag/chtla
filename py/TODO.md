TODO

* detect duplicate states
  if the same processes have run resulting in the same value of state, it's a dup
  can dedup on chooser add exec or maybe during bfs on a per level dedup pass
  could sort the processes that have run to simplify matching
* support mid-function await -- shouldn't be much different than label, it's
  more just making sure the awaitfn is dealt with ok


* TODO add process name by default to recording chooser things recorded
  both .record() and .choose()
* TODO maybe make a parameters object?
* TODO stuttering detection and temporal/liveness checking
  ** DONE <> invariant
  ** TODO []
  ** DONE <>[]
  <>, [], and <>[] equivalents


---- DONE THINGS ------
* DONE Need breadth first search mode. On choosing new: add all executions and throw an sentinel exception that the runner catches.
* NOPE do I need checks in Process?
* DONE add fair and unfair processes
* DONE detect deadlock 

```python
while True:
    can_step = [p for p in checker.processes if not p.is_done()]
```
at any step, one of the choices should be whatever process is chosen to step,
to instead set it to done.
* NOPE make a specific args part of Process and they run first
