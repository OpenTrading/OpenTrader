# -*- coding: utf-8 -*-
import sys
import traceback

# from oerpscenario

__all__ = ['puts', 'set_trace']    # + 20 'assert_*' helpers


def print_exc():
    """Print exception, and its relevant stack trace."""
    tb = sys.exc_info()[2]
    length = 0
    while tb and '__unittest' not in tb.tb_frame.f_globals:
        length += 1
        tb = tb.tb_next
    traceback.print_exc(limit=length)

def _get_context(level=2):
    caller_frame = sys._getframe(level)
    while caller_frame:
        try:
            # Find the context in the caller's frame
            varname = caller_frame.f_code.co_varnames[0]
            ctx = caller_frame.f_locals[varname]
            if ctx._is_context:
                return ctx
        except Exception:
            pass
        # Go back in the stack
        caller_frame = caller_frame.f_back


def puts(oCtx, *args):
    """Print the arguments, after the step is finished."""
    # Append to the list of messages
    oCtx._messages.extend(args)

# From 'nose.tools': https://github.com/nose-devs/nose/tree/master/nose/tools

def set_trace():
    """Call pdb.set_trace in the caller's frame.

    First restore sys.stdout and sys.stderr.  Note that the streams are
    NOT reset to whatever they were before the call once pdb is done!
    """
    import pdb
    for stream in 'stdout', 'stderr':
        output = getattr(sys, stream)
        orig_output = getattr(sys, '__%s__' % stream)
        if output != orig_output:
            # Flush the output before entering pdb
            if hasattr(output, 'getvalue'):
                orig_output.write(output.getvalue())
                orig_output.flush()
            setattr(sys, stream, orig_output)
    exc, tb = sys.exc_info()[1:]
    if tb:
        if isinstance(exc, AssertionError) and exc.args:
            # The traceback is not printed yet
            print_exc()
        pdb.post_mortem(tb)
    else:
        pdb.Pdb().set_trace(sys._getframe().f_back)


