# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

import sys
from optparse import OptionParser, make_option

from OpenTrader.deps.cmd2plus import remaining_args, ParsedString

lOPTIONS_DEFINED = []
def options(option_list, arg_desc="arg", usage=None):
    '''Used as a decorator and passed a list of optparse-style options,
       alters a cmd2 method to populate its ``opts`` argument from its
       raw text argument.

       Example: transform
       def do_something(self, arg):

       into
       @options([make_option('-q', '--quick', action="store_true",
                 help="Makes things fast")],
                 "source dest")
       def do_something(self, arg, opts):
           if opts.quick:
               self.fast_button = True
       '''
    global lOPTIONS_DEFINED
    import optparse
    import pyparsing
    if not isinstance(option_list, list):
        option_list = [option_list]
    for opt in option_list:
        # opt is an optparse Option
        lOPTIONS_DEFINED.append(pyparsing.Literal(opt.get_opt_string()))
    def option_setup(func):
        optionParser = OptionParser(usage=usage)
        optionParser.disable_interspersed_args()
        for opt in option_list:
            # opt is an optparse Option
            optionParser.add_option(opt)
        optionParser.set_usage("%s [options] %s" % (func.__name__[3:], arg_desc))
        optionParser._func = func

        def oUpdateOptionParser(instance):
            if func.__name__.startswith('do_'):
                sName = func.__name__[3:]
                if hasattr(instance, 'oConfig') and sName in instance.oConfig:
                    oConfigSection = instance.oConfig[sName]
                    # iterate over optionParser
                    for sKey, gVal in oConfigSection.iteritems():
                        sOption = '--' +sKey
                        if optionParser.has_option(sOption):
                            oOption = optionParser.get_option(sOption)
                            # FixMe: only if the default is optparse.NO_DEFAULT?
                            if oOption.default is optparse.NO_DEFAULT:
                                # FixMe: does this set the default?
                                oOption.default = gVal
                                # FixMe: how about this?
                                optionParser.defaults[oOption.dest] = oOption.default
            return optionParser

        def new_func(instance, arg):
            try:
                # makebe return a list and prepend it
                optionParser = oUpdateOptionParser(instance)
                opts, newArgList = optionParser.parse_args(arg.split())
                # Must find the remaining args in the original argument list, but
                # mustn't include the command itself
                #if hasattr(arg, 'parsed') and newArgList[0] == arg.parsed.command:
                #    newArgList = newArgList[1:]
                newArgs = remaining_args(arg, newArgList)
                if isinstance(arg, ParsedString):
                    arg = arg.with_args_replaced(newArgs)
                else:
                    arg = newArgs
            except optparse.OptParseError as e:
                print (e)
                optionParser.print_help()
                return
            if hasattr(opts, '_exit'):
                return None
            result = func(instance, arg, opts)
            return result
        func._optionParser = optionParser
        if func.__doc__ is None and usage is None:
            func.__doc__ = ""
        elif func.__doc__ is None and usage:
            func.__doc__ = usage
        elif usage:
            func.__doc__ = '%s\n%s' % (usage, func.__doc__, )
        new_func.__doc__ = '%s\n%s' % (func.__doc__, optionParser.format_help())
        return new_func

    return option_setup
