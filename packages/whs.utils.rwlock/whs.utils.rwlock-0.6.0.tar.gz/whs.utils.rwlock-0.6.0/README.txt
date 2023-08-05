This is internal company implementation of lock, that allows only one kind of
operation be executed at the time (reading or writing). Any number of callers
can acquire reading or writing at once, but if someone tries to acquire writing
while reading is acquired, it will wait, until all readers that acquired lock
release it (and vice versa).

At the moment it works only with threading, but few simple modifications will
result in multiprocessing-enabled implementation.

whs.utils.rwlock is a package, but should be used as a module (all code is in
__init__.py).


If you want to develop this, remember to switch to branch develop.

On this branch main package is named whs_dev.
If it wasn't, other installed packages would be shadowed by local package whs.

When merging develop to master, remember to change whs_dev to whs.