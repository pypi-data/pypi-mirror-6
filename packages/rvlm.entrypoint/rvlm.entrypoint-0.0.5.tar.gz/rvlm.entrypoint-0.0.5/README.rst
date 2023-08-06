This module may be helpful in writing small and clear scripts, with no ugly
command line parsing code, as it has the following features:

* Automatically generate argument parsers basing on "main" function signature
  and docstring.
* Automatically run the "main" function when a script is called directly,
  but not when it is included as a module.

Right after this module was written, its author discovered for himself
the `entrypoint` module (https://pypi.python.org/pypi/entrypoint). But it
appeared to be that original `entrypoint` behaves sometimes in a strange
way. So, it was decided to continue development, and also to rename this module
to `rvlm.entrypoint` from former `rvlm.argmap`, becase this name
sounds better still doesn't introduce names conflict by having a prefix.
