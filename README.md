# CHTLA

A model checking framework on top of https://github.com/drewcsillag/chooser, but copying the library over
The library in python is mostly the same, but supports breadth first search

Also realizing that python gets pretty slow pretty quickly for even simplish models -- if you change the
number of threads or the buffer size in augagile.py, it can quickly get to running for hours, so there
will be a rust version of this soon. I just wanted to prove what I claimed [here](https://drew.thecsillags.com/posts/2022-12-27-choosing-everything/)
where I said 
> After thinking about it more, it could be used to do formal verification, since what TLA+ does is search the state space of the system specified in TLA+ or PlusCal (because raw TLA+ is pretty terrible, though PlusCal isn’t great either)

Having dug into TLA+ and PlusCal more, TLA+ is even worse than I remembered. PlusCal is notably less bad. But I think something that makes
formal verification less accessible is literally that the standard tooling for TLA+/PlusCal is pretty awful. I'm hoping to make it less so
with the rust version.