# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

"""
Configuration for behave test runner.
"""

import sys, os
from support import tools

# we may need this to run the tests in the source directory uninstalled
sRootDir = os.path.dirname(os.path.dirname(__file__))
if sRootDir not in sys.path:
    sys.path.insert(0, sRootDir)
del sRootDir

def before_step(ctx, step):
    ctx._messages = []
    # Extra cleanup (should be fixed upstream?)
    ctx.table = None
    ctx.text = None

def after_step(ctx, laststep):
    if ctx._messages:
        # Flush the messages collected with puts(...)
        if hasattr(ctx.config, 'output'):
            output = ctx.config.output
            for item in ctx._messages:
                for line in str(item).splitlines():
                    output.write(u'      %s\n' % (line,))
            # output.flush()
        elif hasattr(ctx.config, 'outputs'):
            # FixMe: ctx.config.outputs is a list of StreamOpener instances
            for output in ctx.config.outputs:
                if not hasattr(output, 'stream'): continue
                for item in ctx._messages:
                    for line in str(item).splitlines():
                        output.stream.write(u'      %s\n' % (line,))
                # output.flush()
        else:
            pass
        
    if laststep.status == 'failed' and ctx.config.stop:
        # Enter the interactive debugger
        tools.set_trace()
