#!/usr/bin/env python
# coding: utf-8
"""
Logging
"""

# Python Standard Library
import datetime
import importlib
import inspect
import sys
import types

#
# Metadata
# ------------------------------------------------------------------------------
#
__project__ = "logfile"
__author__ = u"Sébastien Boisgérault <Sebastien.Boisgerault@mines-paristech.fr>"
__license__ = "MIT License"
__url__     = "https://github.com/boisgera/logfile"
__version__ = "0.2.2"
__classifiers__ = """
Intended Audience :: Developers
Operating System :: OS Independent
Programming Language :: Python :: 2.7
License :: OSI Approved :: MIT License
Topic :: Software Development :: Libraries :: Python Modules
Topic :: System :: Logging
"""

# ------------------------------------------------------------------------------
# TODO: for C/optimized code, issue a sub-module ("raw_logfile" for example ?
#       that can be used in place of the logfile. Frame trickeries are disabled,
#       naming has to be done manually. (Doable ?)
#
# TODO: *shared* configuration between all loggers to make logging cooperative.
#
# Design: given that all existing loggers shall *implicitly* refer to the config
#         (that holds for example the verbosity level), we have no choice
#         but to have a global module-level variable here. However, a user
#         of the logger module that intends to play nice and not scramble other
#         logger users may need some get/set config functions.       

# Doc: the global _Config instance has the following properties: 
#      - 'level' is a verbosity level: the higher it is, the more gets printed.
#      - 'output' is the common loggers output file object,
#      - 'format' is the customizable message formatting method. It may use
#        (the source logger object and) the message logged.
#      - [TODO]: 'filters': I'd like to have the way to specify a set of
#        (positive or negative ?) filters that may filter according to the
#        hierarchy of loggers context (say 'mystuff.deeper.blah') optionnaly
#        inferred at loggers creation time by the __main__ variable ?
#        CARE: this inference won't work if the module is used as a script ...
#        (doctest stuff may be affected)

# TODO: generalize the context so that we may say for example that we are in
#       audio.wave.write (function write in the audio.wave module) ? Dynamic
#       contexts ? That would be nice and quite easy I guess if I use
#       context managers.
#
# TODO: document automatic substitution of local variables in messages.
#
# TODO: have a look at 
# <http://stackoverflow.com/questions/4492559/python-code-to-get-current-function-into-a-variable> to get the (qualified) name of a function/method
# that is currently executed. Use it as an info for the logger context and
# drop explicit context naming ? Migrate the standard logfiles to the
# module toplevel ?

# TODO: register modules: build a code to qualified name map.

# TODO: use the inspiration from warnings module to extract more info from
#       the point of call (module, that could be the default tag, line, etc.)
#       Probably use the module info as the default tagging information to
#       limit the need for manual tagging ? By a suitable exploration of the
#       code object, we can even get to the function name. Would it work
#       for methods (get the class name ?). Nope. Same issue for methods
#       that we have for profiling, would require (SOME) source file
#       analysis (and does not always work ...). What about generated methods
#       or methods added in a class after its definition ? (Would not work
#       with source analysis right ?). Do the opposite and inspect all methods
#       of all classes in a module to identify them by code (code object I
#       mean) ? But that won't work with decorators or generated functions ...
#       I am not sure how, i should deal with that issue (and I am not sure
#       that both issues are the same). With an explicit
#       "logfile.tag" context manager ?
#       Mmm even for inner function, we still have the name. And that may
#       be good enough ? Otherwise we could find something with the lineno
#       if it is in the range of a function def or decorator ? And here,
#       we would have little choice but parsing ? Use getsourcelines from
#       inspect to do the job ? Use syntaxic analysis on top of that ?
#       Well maybe in a first approach, only deal with classes ? Or dont
#       even bother ?
#
#       Rk: it's hard to implement a system in which manual tagging can
#           override the automatic tagging ... How do we know if the
#           tagging was set for the current function or the previous one
#           in the call stack ? Fully automatic would be better ... (?)

# TODO: study the warnings API. Disable the warnings by default ? (would be
#       kind of redundant ?). Yes, but only in logfile.warning calls, restore
#       the filter state after that. Implement pre-post hooks as context
#       managers ?
#       ABOUT WARNINGS: logfile should probably NOT integrate warnings,
#       because some features would be redundant (filters, print to
#       stdout, etc.). The ability to turn warnings into errors could
#       be easily programmed in each module that needs it, and controlled
#       by a global function (think of `seterr` in `numpy`). No need to
#       offer that in logfile ...

# TODO: implement the full local / global / builtin namespaces in templating.

# TODO: replace the general hook system with an hardcoded system ? Hook only
#       for critical an error for the moment ?

#
# Logger API
# ------------------------------------------------------------------------------
#

class LogFile(int):
    """
    LogFiles are files used to log messages.

    TODO: talk about the level / int stuff and configuration after the
          files properties ?

    LogFiles also behave like integers: the number they represent denotes how 
    important their messages are. The lower the logfile number, the more 
    important the logfile. Five standard log files are defined:

        >>> import logger
        >>> names = "critical error warning info debug"
        >>> for name in names.split():
        ...     logfile = getattr(logger, name)
        ...     print "{0:>8}: {1:>2}".format(name, int(logfile))
        critical: -2
           error: -1
         warning:  0
            info:  1
           debug:  2

    **TODO: migrate the config.level discussion to the config part, with
    format and output discussion**

    A message written into a logfile will effectively get logged only 
    if the logfile number is less or equal to the current verbosity 
    (`config.level`). For example, with the default logger 
    verbosity (`0`), only messages send to the `critical`, `error` 
    and `warning` logfiles will logged. As logfiles are integers, they
    may be used directly to change the logger verbosity: the code

        >>> logger.config.level = logger.info

    will increase the verbosity to `1`, so that the messages to the `info`
    are now logged. **TODO: test before after**

    #### Writing into LogFiles

    To demonstrate how logging works, we first make sure that the output of
    the logfiles are `sys.stdout` instead of the default `sys.stderr`

        >>> import sys
        >>> logger.config.output = sys.stdout

    Messages can be send to logfiles in two ways: either using the file 
    interface, such as in:

        >>> print >> logger.warning, "I feel a disturbance in the Force."
        I feel a disturbance in the Force.

    or using the callable interface:

        >>> logger.warning("I feel a disturbance in the Force.")
        I feel a disturbance in the Force.


    The former call is handy to quicky convert a code full of  `print` 
    statements without any hierarchy into the `logger` style 
    of logging. 

    #### Message Variables 

    The message send to logfiles often depends on the value of some local
    variables. To simplify this use case, we may refer to local variables
    in messages with the same curly brace syntax use by the 
    [string.format method][format]. The value of the variable will be
    automatically substituted into the message. For example:

        >>> jedi = "Luke"
        >>> logger.info("Use the Force, {jedi}.")
        Use the Force, Luke.

    [format]: http://docs.python.org/library/string.html#formatstrings

    #### LogFile Hooks

    LogFile hooks are an easy way to trigger some action when some message
    is sent to a logfile. A typical use case is to automatically raise an 
    Exception when a message is sent to the `error` logfile:

    First, we disable logging of `error` messages and set the exception hook:

        >>> logger.config.level = logger.critical
        >>> def raise_exception(message):
        ...     raise Exception(message)
        >>> logger.error.set_hook(raise_exception)

    Now, if we use the logfile `logger.error`, we obtain:

        >>> logger.error("I feel a great disturbance in the Force.")
        Traceback (most recent call last):
        ...
        Exception: I feel a great disturbance in the Force.

    LogFile hooks will use extra arguments in logfile calls, for example:

        >>> def raise_exception(message, type=Exception):
        ...     raise type(message)
        >>> logger.error.set_hook(raise_exception)
        >>> class ForceError(Exception):
        ...     pass
        >>> logger.error("I feel a great disturbance in the Force.", ForceError)
        Traceback (most recent call last):
        ...
        ForceError: I feel a great disturbance in the Force.
"""
    def __new__(cls, name, number, hook=None):
        return int.__new__(cls, number)

    def __init__(self, name, number, hook=None):
        self.name = name
        self.hook = hook

    def get_tag(self, message, *args, **kwargs):
        tag = kwargs.get("_tag")
        if tag is None:
            _frame_depth = kwargs.get("_frame_depth") + 1

            tag_parts = []          
            frame = inspect.currentframe(_frame_depth)
            if frame is None:
                raise ValueError("can't get the caller frame")
            module = inspect.getmodule(frame.f_code)
            if module is not None:
                module_name = module.__name__
                if module_name == "__main__":
                    app_name = getattr(module, "__project__", None)
                    if app_name:
                        tag_parts.append(app_name)
                else:
                    tag_parts.append(module_name)
            function_name = frame.f_code.co_name
            # Logfiles can be called at the module level, get rid of <module>
            if function_name != "<module>": 
                tag_parts.append(function_name)
            tag = ".".join(tag_parts)
        return tag

    def get_message(self, message, *args, **kwargs):
        _frame_depth = kwargs.get("_frame_depth") + 1
        frame = inspect.currentframe(_frame_depth)
        if frame is None:
            raise ValueError("can't get the caller frame")
        locals_ = frame.f_locals
        message = str(message).format(**locals_)
        if message.endswith("\n"):
            message = message[:-1]
        return message

    def write(self, message):
        self(message, _frame_depth=1)

    def __call__(self, message, *args, **kwargs):
        # the locals() from the user code are always 2 frames away.
        # ISSUE: when logger logfiles are used from Cython code, 
        #        there is no corresponding frame and we can't get
        #        to the locals ... we end up with a 'ValueError' 
        #        instead. 
        # Detect that frames do not work, let the use know about it ?
        # Let him enable/disable frame + locals() magic based on this
        # information ? That sucks ... writing two versions of the same
        # code is not a solution !

        # TODO: delay the inspect hackery until we know that we have to
        #       write something (performance reasons) or that some hooks
        #       require us to evaluate the message.

     # TODO: template substitution / namespace finding and tag finding
     #       / analysis from arguments COULD be dispatched in methods so
     #       that derived classes could implement non-standard (simpler ?)
     #       schemes. Then, where/when do we try to get the frame ? We
     #       Don't want to ask for it if that's not needed and we don't
     #       want to ask for it twice either ? Arf, calling is twice is
     #       probably not a big deal. But we need to give _depth along ?
     #       Urk, that's hard on the implementer of new methods. Too bad :)


        kwargs["_frame_depth"] = kwargs.get("_frame_depth", 0) + 1
        message = self.get_message(message, *args, **kwargs)
        tag = self.get_tag(message, *args, **kwargs)
        date = datetime.datetime.now() # make a get_date method ?
        item = dict(logfile=self, message=message, tag=tag, date=date)

        kwargs.pop("_tag", None)
        kwargs.pop("_frame_depth", None)

        if config.level >= self:
            config.output.write(config.format(**item))
            try:
                config.output.flush()
            except AttributeError:
                pass
        hook = self.hook
        if hook is not None:
            hook(message, *args, **kwargs) # use (item, *args, **kwargs) instead ?
            # or (message, logfile, tag, date, *args, **kwargs ?) or
            # (logfile (aka self), message, ...) ?

    def __str__(self):
        return self.name

    __repr__ = __str__ # more explicit ?

#
# Standard LogFiles
# ------------------------------------------------------------------------------
#

def critical_hook(message, status=None):
    # If the status matters, override the message.
    if status is not None:
        sys.exit(status)
    else:
        sys.exit(message)

def error_hook(message, type=ValueError, *args):
    raise type(message, *args)

critical = LogFile("critical", -2, hook=critical_hook)
error    = LogFile("error"   , -1, hook=error_hook)
warning  = LogFile("warning" ,  0)
info     = LogFile("info"    ,  1)
debug    = LogFile("debug"   ,  2)  

#
# Shared Configuration
# ------------------------------------------------------------------------------
#

class Config(object):
    """
    Logging Configuration
    """
    def __init__(self, level=None, output=None, format=None):
        """
        The members of a `Config` instance are:

        `level:`
          : is verbosity level: the higher it is, the more gets logged,
        `output:`
          : the common logger logfiles output file object,
        `format:` 
          : the customizable message formatting function whose
            arguments are:
            
            `logfile:`
              : the logfile that requested the logging, 
            `message:`
              : the message logged.
        """
        self.level = level or 0
        self.output = output or sys.stderr
        self.format = format or self._format
    def _format(self, logfile, message, tag):
        return message + "\n"

config = Config()

#
# Formatters
# ------------------------------------------------------------------------------
#

# TODO: provide a choice of formatters ?

# tmp / DEBUG
def _format(**kwargs):
    kwargs["date"] = kwargs["date"].strftime("%Y/%m/%d %H:%M:%S")
    # BUG: if i don't REPR the logfile, it ends up as an int ??? WTF ?
    # TODO: manage multi-line messages.
    # tag-length dependent padding or not ?
    pad = 20 * " " + " " + 11 * " " + " " + 18 * " " + "|" + " "
    return "{date} | {logfile!r:<9} | {tag:<16} | {message}\n".format(**kwargs)

config.format = _format

#
# Unit Tests
# ------------------------------------------------------------------------------
#
if __name__ == "__main__":
    import doctest
    doctest.testmod()

