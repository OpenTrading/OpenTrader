#!/bin/sh
#  Test the communications with Mt4 via RabbitMQ;
#  these tests NEED to have BOTH RabbitMQ and Mt4 running
ps ax | grep -iq terminal.exe || { echo "AssertionERROR: we NEED Mt4 running" ; exit 1 ; }

# The calling of OTCmd2 may need to be customized for your setup:
if [ -z "$OTPYTHON_EXE" ] ; then
    export OTPYTHON_EXE="sh /c/bin/tpython.sh"
fi

if [ -z "$OTCMD2" ] ; then
    export OTCMD2="$OTPYTHON_EXE OpenTrader/OTCmd2.py"
fi
#  We need to know where you have your metatrader installed.
if [ -z "$OTMT4_DIR" ] ; then
    export OTMT4_DIR="/c/Program Files/MetaTrader"
fi
[ -d "$OTMT4_DIR" ] || { echo "AssertionError: directory not found: " "$OTMT4_DIR" ; exit 6 ; }

# We run these tests in this directory of the source distribution
if [ ! -f setup.py -o -f test.sh ] ; then
    cd ../..
fi
[ ! -f setup.py -o -f test.sh ] && exit 8

# we put the output in tmp/logs
if [ -z "$OTLOG_DIR" ] ; then
    export OTLOG_DIR="tmp/logs"
  fi
[ -d "$OTLOG_DIR" ] || mkdir "$OTLOG_DIR" || exit 4

$OTCMD2 -P "$OTMT4_DIR" < share/examples/OTCmd2-sub.txt \
	  2>&1|tee "$OTLOG_DIR"/OTCmd2-sub.log

$OTCMD2 -P "$OTMT4_DIR" < share/examples/OTCmd2-chart.txt \
	  2>&1|tee "$OTLOG_DIR"/OTCmd2-chart.log

$OTCMD2 -P "$OTMT4_DIR" < share/examples/OTCmd2-pub_wait.txt \
	  2>&1|tee "$OTLOG_DIR"/OTCmd2-pub_wait.log

$OTCMD2 -P "$OTMT4_DIR" < share/examples/OTCmd2-pub_wait-Accounts.txt \
	  2>&1|tee "$OTLOG_DIR"/OTCmd2-pub_wait-Accounts.log

$OTCMD2 -P "$OTMT4_DIR" < share/examples/OTCmd2-pub_wait-jOT.txt \
	  2>&1|tee "$OTLOG_DIR"/OTCmd2-pub_wait-jOT.log

$OTCMD2 -P "$OTMT4_DIR" < share/examples/OTCmd2-ord.txt \
	  2>&1|tee "$OTLOG_DIR"/OTCmd2-ord.log
