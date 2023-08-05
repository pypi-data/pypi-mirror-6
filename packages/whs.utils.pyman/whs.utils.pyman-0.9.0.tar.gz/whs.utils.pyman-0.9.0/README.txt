This is simple module created with intention of easier help system development
for your applications.

Standard usage should mimic POSIX man program, basing on builtin help()
implementation.

It was tested on python 3.3, but was written with any version in mind.


If you want to develop this, remember to switch to branch develop.

On this branch main package is named whs_dev.
If it wasn't, other installed packages would be shadowed by local package whs.

When merging develop to master, remember to change whs_dev to whs.