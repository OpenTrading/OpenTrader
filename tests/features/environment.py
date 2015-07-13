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

def before_all(oCtx):
    if not hasattr(oCtx, 'userdata'):
        oCtx.userdata = dict()
    oCtx.userdata['oMain'] = None

def before_step(oCtx, step):
    oCtx._messages = []
    # Extra cleanup (should be fixed upstream?)
    oCtx.table = None
    oCtx.text = None

def after_step(oCtx, laststep):
    if oCtx._messages:
        # Flush the messages collected with puts(...)
        if hasattr(oCtx.config, 'output'):
            output = oCtx.config.output
            for item in oCtx._messages:
                for line in str(item).splitlines():
                    output.write(u'      %s\n' % (line,))
            # output.flush()
        elif hasattr(oCtx.config, 'outputs'):
            # FixMe: oCtx.config.outputs is a list of StreamOpener instances
            for output in oCtx.config.outputs:
                if not hasattr(output, 'stream'): continue
                for item in oCtx._messages:
                    for line in str(item).splitlines():
                        output.stream.write(u'      %s\n' % (line,))
                # output.flush()
        else:
            pass
        
    if laststep.status == 'failed' and oCtx.config.stop:
        # Enter the interactive debugger
        try:
            tools.set_trace()
        finally:
            # This seems to be *required* - after_all is not called after here.
            vEnvAtexit(oCtx, "after_step calling oMain.vAtexit")

def vEnvAtexit(oCtx, sMsg):
    if 'oMain' in oCtx.userdata and oCtx.userdata['oMain']:
        if 'verbose' in oCtx.userdata and int(oCtx.userdata['verbose']) >= 4:
            # FixMe: why am I not seing this message?
            sys.stdout.write(sMsg +'\n')
            sys.stdout.flush()
        oCtx.userdata['oMain'].vAtexit()
        #? del?
        oCtx.userdata['oMain'] = None

def after_all(oCtx):
    """
    If we have called vTestCreated and created an OTCmd2 instance,
    and if the instance has launched a listening thread, then
    it must be terminated cleanly or it weill hang the test runner.
    Usually this is done by vTestDestroy. But if we error, including
    if we error and drop into the debugger, we must still run the
    OTCmd2 instance vAtexit method.
    """
    if 'oMain' in oCtx.userdata and oCtx.userdata['oMain']:
        try:
            vEnvAtexit(oCtx, "after_all calling oMain.vAtexit")
        except Exception, e:
            sys.stdout.write("Error when calling oMain.vAtexit: " +str(e))
        finally:
            #? del?
            oCtx.userdata['oMain'] = None
            
