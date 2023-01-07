TODO

* TODO do I need checks in Process?
* TODO add process name by default to recording chooser things recorded
  both .record() and .choose()
* TODO maybe make a parameters object?
* TODO stuttering detection and temporal/liveness checking
  <>, [], and <>[] equivalents
  -- Have processes drop dead

```python
while True:
    can_step = [p for p in checker.processes if not p.is_done()]
```
at any step, one of the choices should be whatever process is chosen to step,
to instead set it to done.