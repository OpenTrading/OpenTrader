#!/bin/sh
#  These examples can be run as a test suite, but some are slow
#  and some require the rabbitq server to be running and some
#  require a Metatrader to be running with a OTPyTestPikaEA.mq4 EA loaded.
#  
#  We will try to break the examples up into groups to be run under different conditions
#  This script is in Unix bash and should run under Windows using MSYS.
#  Or maybe someone can kindly convert it to MSDOS BAT and upload it to githib.com
#  
#  We need to know where you have your metatrader installed.
#  
if [ -z "$OTMT4_DIR" ] ; then
    export OTMT4_DIR="/c/Program Files/MetaTrader"
fi
#  
#  The calling of OTCmd2 may need to be customized for your setup.
if [ -z "$OTPYTHON_EXE" ] ; then
    export OTPYTHON_EXE="sh /c/bin/tpython.sh"
fi

if [ -z "$OTCMD2" ] ; then
    export OTCMD2="$OTPYTHON_EXE OpenTrader/OTCmd2.py"
fi

# We run these tests in this directory of the source distribution
if [ ! -f setup.py -o -f test.sh ] ; then
    cd ../..
fi

# we put the output in tmp/logs
if [ -z "$OTLOG_DIR" ] ; then
    export OTLOG_DIR="tmp/logs"
  fi
[ -d "$OTLOG_DIR" ] || mkdir "$OTLOG_DIR" || exit 4

sh share/examples/test_rabbitmq_running.sh || exit 10
sh share/examples/test_backtest.sh || exit 11
sh share/examples/test_mt4_rabbitmq_running.sh || exit 12

# There should be no AssertionError in the logs
grep AssertionError "$OTLOG_DIR"/*log && exit 3

# There should be no Timeouts in the logs
grep "WARN: No retval returned in" "$OTLOG_DIR"/*log && exit 4


