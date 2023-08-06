# -*- coding: utf-8 -*-
"""
rvlm.entrypoint: automatic argument parser for functions
========================================================

Converts function's arguments to getopt-style command line options and
arguments. This may definitely help in writing small and clear scripts, with
no ugly command line parsing code.

This module can:

  * Automatically generate argument parsers basing on "main" function signature
    and docstring.
  * Automatically run the "main" function when a script is called directly,
    but not when it is included as a module.

Right after this module was written, its author discovered for himself
the :mod:`entrypoint` module (https://pypi.python.org/pypi/entrypoint). But it
appeared to be that original :mod:`entrypoint` behaves sometimes in a strange
way. So, it was decided to continue development, and also to rename this module
to :mod:`rvlm.entrypoint` from former :mod:`rvlm.argmap`, becase this name
sounds better still doesn't introduce names conflict by having a prefix.

:copyright: 2014, Pavel Kretov
:license: MIT
"""
import argparse
import inspect
import re
import string
import sys


class ParserError(Exception):
    """
    Exception raised when wrong command line arguments are given. It is only
    raised by :func:`call` with `raiseOnError` set to :const:`True`. Overwise,
    :func:`sys.exit` gets called.
    """
    pass


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ParserError(message)


def call(func,
         args         = None,
         emptyVarArgs = True,
         helpOptions  = True,
         shortOptions = True,
         docStrings   = True,
         changeNames  = True,
         raiseOnError = True):
    """
    Convert function `func` argument convention to command line options
    and runs it with converted arguments.

    :param func: Function to be run. Must have parameter information available
        through inspection. It also must not have `**kwargs` parameter.

    :param args:
        Getopt-style command line parameters. It is a list of command line
        options and arguments mostly like sys.argv array, but unlike it without
        first item (:obj:`sys.argv[0]`) which commonly contains script name.
        Default value :const:`None` means that :obj:`sys.argv` will be used
        to get that list.

    :param emptyVarArgs:
        Specifies whether target function 'func' can take empty arguments
        list as its `*vararg` parameter. Default value :const:`True` represents
        the fact that there is no way to set this restriction in Python syntax.
        But setting it to :const:`False` will require at least one getopt-style
        argument to be passed as `*vararg` (if it is present, of course).

    :param helpOption:
        Specifies whether to generate :option:`--help` (and :option:`-h`)
        option or not. Default value is :const:`True` which means help option
        will be enabled. Setting this to :const:`False` will disable help
        messages and also will make shorthand :option:`-h` available for
        use by another option (see parameter `shortOptions` for more info).

    :param shortOptions:
        Enables automatic generation of short options. Short options will be
        the first letters of arguments name comverted to lower case. If several
        optional arguments start with the same letter, no short option will be
        generated. Default value is :const:`True`. Note that short option
        :option:`-h` is reserved for help message display if `helpOption`
        parameter is set to :const:`True`.

    :param docStrings:
        Try to find parameters description in function's docstring
        (:obj:`__doc__`). Description are found using very simple regular
        expression, so this feature may fail sometimes. For this to work
        parameters must be described on separate lines like in the following::

            \"\"\"
            * cmd Command to run interactively.
            - cmd Command to run interactively.
            * cmd: Command to run interactively.
            *** cmd - Command to run interactively.
            :param cmd: Command to run interactively.
            @param cmd Command to run interactively.
            \"\"\"

        where `cmd` must be the *exact* parameter name. Some more variants are
        available, though. Default value is :const:`True`.

    :param changeNames:
        Enables automatic arguments renaming. Setting this to :const:`True`
        will change naming convention of function arguments to dash-style. For
        the following example function::

            def func(logFile=None, StartDate=None, stop_at_exit=False):
               pass;

        arguments will be converted to :option:`--log-file`,
        :option:`--start-date` and :option:`--stop-at-exit`. But the usage
        clause will look something like this::

            Usage: func.py [--log-file LOG_FILE] [--start-date START_DATE] ...

    :param raiseOnError:
        Specifies whether to raise :exc:`ParserException` when given command
        line arguments `args` cannot be parsed to function `func` parameters.
        If this value is set to :const:`False`, :func:`sys.exit` is called
        instead. Default value is :const:`True`.

    :returns:
        Function conveys return value from target function `func`.

    """
    # There is no assertion for args here, because it must involve checking
    # whether all items are strings which will make the code ugly if intended
    # support for both Python 2.7 and 3. Leave the check to 'argparse'.
    assert(callable(func))
    assert(isinstance(emptyVarArgs, bool))
    assert(isinstance(helpOptions,  bool))
    assert(isinstance(shortOptions, bool))
    assert(isinstance(docStrings,   bool))
    assert(isinstance(changeNames,  bool))

    # First argument which is the script name must be thrown away
    # for 'argparse' to work.
    if args is None:
        args = sys.argv[1:]


    funcDoc = func.__doc__
    def paramDoc(funcArg):
        if not docStrings or funcDoc is None:
            return None

        match = re.search(
            "^\\s*[:@*-]*\\s*(param:?)?\\s+%s\\s*[:-]*\\s*(.+)$"
            % funcArg, funcDoc, re.MULTILINE | re.UNICODE)

        if match is None:
            return None

        return match.group(2)


    def optionName(arg):
        result = re.sub("([a-z])([A-Z])", "\\1-\\2", arg)
        result = result.replace("_", "-")
        result = re.sub("-+", "-", result)
        result = result.lstrip("-")
        result = result.lower()
        return result


    def metaName(arg):
        return optionName(arg).replace("-", "_").upper()


    # Simulate behavior of 'inspect.getfullargspec' in old Pythons
    # using deprecated 'getargspec'.
    getfullargspec = None
    if sys.version_info >= (3, 0):
        getfullargspec = inspect.getfullargspec
    else:
        getfullargspec = lambda f: inspect.getargspec(f) + ([], None, None)

    # Get arguments specification through inspection.
    (funcArgs, funcVarArg, funcKwVarArgs, funcDefs,
        funcKwOnlyArgs, funcKwOnlyDefs, _) = getfullargspec(func)

    if funcKwVarArgs is not None:
        raise RuntimeError("Functions with **kwargs are not supported,")

    if funcArgs is None: funcArgs = []
    if funcDefs is None: funcDefs = []
    if funcKwOnlyArgs is None: funcKwOnlyArgs = []
    if funcKwOnlyDefs is None: funcKwOnlyDefs = {}
    nfuncDefs = len(funcDefs)

    # Build all available information about named and positional arguments
    # in the following two lists.
    funcPosArguments = funcArgs[:-nfuncDefs]
    funcKwdArguments = []
    for (arg, val) in zip(funcArgs[-nfuncDefs:], funcDefs):
        funcKwdArguments.append((arg, val, False))

    for arg in funcKwOnlyArgs:
        if arg in funcKwOnlyDefs:
            funcKwdArguments.append((arg, funcKwOnlyDefs[arg], False))
        else:
            funcKwdArguments.append((arg, None, True))

    # Look for options which names can be unambigously reduced to first
    # letters only.
    parserShortOptions = set()
    if shortOptions:
        shorts = {}
        for (arg, _, _) in funcKwdArguments:
            fst = arg[0].lower()
            if fst not in string.ascii_lowercase: continue
            shorts[fst] = arg if fst not in shorts else None

        # Short option '-h' is conventionally used as a shorthand for '--help'.
        # In most cases there is no need to change this behavior.
        if helpOptions and ("h" in shorts):
            del shorts["h"]

        parserShortOptions = set(shorts.values())

    # Now create arguments parser and feed it with rules.
    parser = None
    if raiseOnError: parser = _ArgumentParser(add_help = helpOptions)
    else: parser = argparse.ArgumentParser(add_help = helpOptions)

    for (arg, val, req) in funcKwdArguments:
        optName   = optionName(arg)
        optLetter = arg[0].lower()

        names = ["--" + optName]
        if arg in parserShortOptions:
            names.append("-" + optLetter)

        if isinstance(val, bool):
            negNames = ["--no-" + optName]
            if arg in parserShortOptions:
                negNames.append("-" + optLetter.upper())

            group = parser.add_mutually_exclusive_group()
            group.add_argument(*names,
                dest     = arg,
                default  = [val],
                action   = "store_const",
                const    = [True],
                help     = paramDoc(arg))
            group.add_argument(*negNames,
                dest     = arg,
                action   = "store_const",
                const    = [False])
        else:
            parser.add_argument(*names,
                dest     = arg,
                default  = [val],
                type     = type(val),
                required = req,
                nargs    = 1,
                metavar  = metaName(arg),
                help     = paramDoc(arg))

    for arg in funcPosArguments:
        parser.add_argument(
            dest    = arg,
            metavar = metaName(arg),
            help    = paramDoc(arg))

    if funcVarArg is not None:
        parser.add_argument(
            dest    = funcVarArg,
            metavar = metaName(funcVarArg),
            nargs   = "*" if emptyVarArgs else "+",
            help    = paramDoc(funcVarArg))

    parsed = vars(parser.parse_args(args))

    for (arg, _, _) in funcKwdArguments:
        parsed[arg] = parsed[arg][0]

    callKwdArgs = {}
    for arg in funcKwOnlyArgs:
        callKwdArgs[arg] = parsed[arg]

    callPosArgs =  [parsed[arg] for arg in funcArgs]
    if funcVarArg is not None:
        callPosArgs += parsed[funcVarArg]

    return func(*callPosArgs, **callKwdArgs)


def mainfunction(**kwargs):
    """
    Runs the function if the module in which it is declared is being run
    directly from the command line. Putting the following before the function
    definition would be similar to::

        if __name__ == '__main__':
            func()

    This will work most expectedly as the outermost decorator, as it will call
    the function before any more outwards decorators have been applied.
    """
    def wrapper(func):
        frame_local = sys._getframe(1).f_locals
        if '__name__' in frame_local and frame_local['__name__'] == '__main__':
            call(func, raiseOnError=False, **kwargs)
        return func

    return wrapper
