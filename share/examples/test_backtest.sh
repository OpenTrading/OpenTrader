#!/bin/sh

# These tests do not need to have either RabbitMQ or Mt4 running:
# we need to know where you have your metatrader installed.
if [ -z "$OTMT4_DIR" ] ; then
    export OTMT4_DIR="/c/Program Files/MetaTrader"
  fi
if [ ! -d "$OTMT4_DIR" ] ; then
    echo "AssertionError: we need to know where you have your metatrader installed"
    exit 6
  fi

# The calling of OTCmd2 may need to be customized for your setup:
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

#  You MUST have created a CSV file for the tests to work on.
if [ ! -f tmp/EURUSD60-2014.csv ] ; then
    echo "AssertionError: create a CSV file for the tests to work on"
    exit 5
  fi

# We put the output in tmp/logs
if [ -z "$OTLOG_DIR" ] ; then
    export OTLOG_DIR="tmp/logs"
  fi
[ -d "$OTLOG_DIR" ] || mkdir "$OTLOG_DIR" || exit 4

${OTCMD2} -P "$OTMT4_DIR" < share/examples/OTCmd2-backtest_SMARecipe.txt \
	  2>&1|tee "$OTLOG_DIR"/OTCmd2-backtest.log

${OTCMD2} -P "$OTMT4_DIR" < share/examples/OTCmd2-backtest_recipe.txt \
	  2>&1|tee "$OTLOG_DIR"/OTCmd2-backtest_recipe.log

[ -f tmp/EURUSD60-2014.hdf ] && rm -f tmp/EURUSD60-2014.hdf
${OTCMD2} -P "$OTMT4_DIR" < share/examples/OTCmd2-backtest_omlette.txt \
	  2>&1|tee "$OTLOG_DIR"/OTCmd2-backtest_omlette.log
