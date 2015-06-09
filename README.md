# OpenTrader
## Open Trader

# OpenTrader

OpenTrader

https://github.com/OpenTrading/OpenTrader/

This project gives a command-line interpreter to communicate with
an OpenTrading Metatrader-Python bridge enabled MetaTrader
(https://github.com/OpenTrading/OTMql4AMQP/).
You can subscribe to tick, bar, and timer events,
query, open and close orders, and execute Metatrader code remotely.
If you have pyrabbit installed, you can query the AMQP server.

Coming Real Soon Now(TM) is backtesting of trading recipes,
reading Metatrader history into pandas DataFrames, plotting
DataFrames using matplotlib, and live-trading on Metatrader from recipes.

It builds on OTMql4AMQP, and requires that to be installed in your
Metatrader Python as a pre-requisite, if you want to do live trading.
In your Python, you also must have installed Pika:
https://pypi.python.org/pypi/pika/, which must be accessible to your
OTMql4Py (https://github.com/OpenTrading/OTMql4Py/).
You will have to call OTCmd2 with the `-P` option with the
path of your installed Metatrader (e.g. `c:\Program Files\Metatrader`),
or add your installed OTMql4Py Python directory to the `PYTHONPATH`
environment variable (e.g. `c:\Program Files\Metatrader\MQL4\Python`).

**This is a work in progress - a developers' pre-release version.**

The project wiki should be open for editing by anyone logged into GitHub:
**Please report any system it works or doesn't work on in the wiki:
include the Metatrader build number, the origin of the metatrader exe,
the Windows version, and the AMQP server version and version of the Pika.**
This code in known to run under Linux Wine (1.7.x), so this project
bridges Metatrader to RabbitMQ under Linux.

### Installation

You must have `cmd2` installed the Python that runs this script:
see https://bitbucket.org/catherinedevlin/cmd2

You must have `configobj` installed the Python that runs this script:
The up-to-date one is at https://github.com/DiffSK/configobj/

In your Metatrader Python, you also must have installed Pika:
https://pypi.python.org/pypi/pika/

Firstly, install the OTMql4AMQP, OTMql4Py and OTMql4Lib projects from
https://github.com/OpenTrading/ into the Python called by your Metatrader:
* OTMql4AMQP (https://github.com/OpenTrading/OTMql4AMQP/),
* OTMql4Py (https://github.com/OpenTrading/OTMql4Py/), and
* OTMql4Lib (https://github.com/OpenTrading/OTMql4Lib/)

Attach the OTPyTestPikaEA.mq4 to a chart and make sure it's working:
https://github.com/OpenTrading/OTMql4AMQP/MQL4/Experts/OTMql4/OTPyTestPikaEA.mq4

Then (when it gets checked in :-) run 
```
python setup.py
```
to create the OTCmd2 script. Run `OTCmd2 help` (see below).


### Project

Please file any bugs in the issue tracker:
https://github.com/OpenTrading/OpenTrader/issues

Use the Wiki to start topics for discussion:
https://github.com/OpenTrading/OpenTrader/wiki
It's better to use the wiki for knowledge capture, and then we can pull
the important pages back into the documentation in the share/doc directory.
You will need to be signed into github.com to see or edit in the wiki.


## OTCmd2.py

This script can be run from the command line to send commands
to a OTMql4AMQP enabled Metatrader. It will start a command loop to
listen, send commands, or query the RabbitMQ management interface.
It is based on the cmd2 REPL: see cmd2plus.py in `OpenTrader` -
you must have `cmd2` installed the Python that runs this script:
see https://bitbucket.org/catherinedevlin/cmd2

Call the script with `--help` to see the script options,
and Type help at the command prompt to get more help.


The normal usage is:
```
sub run timer# retval.#  - start a thread listening for messages: timer,retval
pub cmd AccountBalance   - to send a command to OTMql4Pika,
                         the return will be a retval message on the listener
sub hide timer           - stop seeing timer messages (just see the retval.#)
orders list              - list your open order tickets
```

Use the `chart` command to
set and query the chart used for messages to and from RabbitMQ.
The chart ID will look something like: oChart_EURGBP_240_93ACD6A2_1

Use the `subscribe` command to suscribe to RabbitMQ topics from the
`OTPyTestPikaEA.mq4` expert advisor.
Common RabbitMQ topic patterns are: # for all messages, tick.# for ticks,
timer.# for timer events, retval.# for return values.
You can choose as specific chart with syntax like:
```
    tick.oChart.EURGBP.240.93ACD6A2.#
```

Use the `publish` command to publish a message via RabbitMQ to a given chart
on a OTMql4Py enabled terminal running the `OTPyTestPikaEA.mq4` expert advisor.
See the library files `MQL4/Libraries/OTMql4OTLibProcessCmd.mq4`
and `OTLibMt4ProcessCmd.mq4` in the OTMql4Py package for the commands
that are supported.

Use the `orders` to list, query, open and close orders in Mt4.

If you have `pyrabbit` installed, and iff the rabbitmq_management plugin
has been installed in your server, you can introspect some useful
information if the HTTP interface is enabled with the `rabbit` command.

### Messaging Format

The messaging to and from OTMql4Py is still being done with a
very simple format:
```
      sMsgType|sChartId|sIgnored|sMark|sPayload
```
where
```
      sMsgType is one of: cmd eval (outgoing), timer tick retval (incoming);
      sChartId is the Mt4 chart sChartId the message is to or from;
      sIgnored is ignored for now, but may become a checksum on the payload;
      sMark is a simple floating point timestamp, with milliseconds;
and   sPayload is command|json... (outgoing) or type|json (incoming),
      where incoming type is one of: bool int double string json.
```
This may breaks if the sPayload args or value contain a | -
we will probably replace this with json or pickled serialization, or kombu.


### Examples

There are some example OTCmd2 command scripts in the `share/examples`
directory that you can run from the command line with the stdin
from these files:

For example, under Msys or Unix this would be:
```
OTCmd2 -P "c:\\Program Files\\MetaTrader"  < tests/OTCmd2-0.test
```
Where the `-P` option is the path to your Metatrader installation
with `OTMql4QQMP` installed.

You should see no assertion errors,  and you should see no timeouts:
```
WARN: No retval returned in 60 seconds
```

Note that you can use this scripting to open and close orders.


## Pandas love Omlettes!

### (And you thought pandas were vegans :-)

There are many steps to making a good Omlette:

1. Get a feed to make ingredients out of.

2. Get a Recipe to make the Omlette.

3. Make the Ingredients from the Recipe and the Feed(s).

4. Find a Chef to give the Recipe and Ingredients to.

5. Have the Chef cook the Recipe and Ingredients in the Oven(Backtester).

6. Enjoy the Servings that come out of the the Oven(Backtester).



usage: OTBackTest.py [-h] [-T] [-P] [-R SRECIPE] [-C SCHEF] [-H SHDFSTORE]
                     [lArgs [lArgs ...]]

give the Symbol Timeframe and Year to backtest The Timeframe is the period in
minutes: e.g. 1 60 240 1440

positional arguments:
  lArgs                 the Symbol Timeframe and Year to backtest (required)

optional arguments:
  -h, --help            show this help message and exit
  -T, --use_talib       Use Ta-lib for chart operations
  -P, --plot_equity     plot the equity curves of the servings
  -R SRECIPE, --recipe SRECIPE
                        recipe to backtest
  -C SCHEF, --chef SCHEF
                        recipe to backtest
  -H SHDFSTORE, --hdf SHDFSTORE
                        store the recipe and servings in an hdf5 store
### OTCmd2 subscribe
```

Subscribe to messages from RabbitMQ on a given topic:
  sub topics            - shows topics subscribed to.
  sub run TOPIC1 ...    - start a thread to listen for messages,
                          TOPIC is one or more Rabbit topic patterns.
  sub hide TOPIC        - stop seeing TOPIC messages (e.g. tick - not a pattern)
  sub show              - list the message topics that are being hidden
  sub show TOPIC        - start seeing TOPIC messages (e.g. tick - not a pattern)
  sub pprint ?0|1       - seeing TOPIC messages with pretty-printing,
                          with 0 - off, 1 - on, no argument - current value
  sub thread info       - info on the thread listening for messages.
  sub thread stop       - stop a thread listening for messages.
  
Common RabbitMQ topic patterns are: # for all messages, tick.# for ticks,
timer.# for timer events, retval.# for return values.
You can choose as specific chart with syntax like:
    tick.oChart.EURGBP.240.93ACD6A2.#

Usage: sub [options] command

Options:
  -h, --help            show this help message and exit
  -c SCHARTID, --chart=SCHARTID
                        the target chart to subscribe to

```
### OTCmd2 publish
```

Publish a message via RabbitMQ to a given chart on a OTMql4Py enabled terminal:
  pub cmd  COMMAND ARG1 ... - publish a Mql command to Mt4,
      the command should be a single string, with a space seperating arguments.
  pub eval COMMAND ARG1 ... - publish a Python command to the OTMql4Py,
      the command should be a single string, with a space seperating arguments.

You wont see the return value unless you have already done a:
  sub run retval.#

Usage: pub [options] command

Options:
  -h, --help            show this help message and exit
  -c SCHARTID, --chart=SCHARTID
                        the target chart to publish to (or: ANY ALL NONE)

```
### OTCmd2 chart
```

Set and query the chart used for messages to and from RabbitMQ:
  list   - all the charts the listener has heard of,
           iff you have already started a listener with "sub run"
  get    - get the default chart to be published or subscribed to.
  set ID - set the default chart ID to be published or subscribed to.
  set    - set the default chart to be the last chart the listener has heard of,
           iff you have already started a listener with "sub run"

The chart ID will look something like: oChart_EURGBP_240_93ACD6A2_1

Usage: chart [options] command

Options:
  -h, --help  show this help message and exit

```
### OTCmd2 order
```

  ord list          - list the ticket numbers of current orders.
  ord info iTicket  - list the current order information about iTicket.
  ord trades        - list the details of current orders.
  ord history       - list the details of closed orders.
  ord close iTicket [fPrice iSlippage]            - close an order;
                    Without the fPrice and iSlippage it will be a market order.
  ord buy|sell sSymbol fVolume [fPrice iSlippage] - send an order to open;
                    Without the fPrice and iSlippage it will be a market order.
  ord stoploss
  ord trail
  ord exposure      - total exposure of all orders, worst case scenario
  

Usage: ord [options] command

Options:
  -h, --help            show this help message and exit
  -c SCHARTID, --chart=SCHARTID
                        the target chart to order with (or: ANY ALL NONE)

```
### OTCmd2 rabbit
```

If we have pyrabbit installed, and iff the rabbitmq_management plugin
has been installed in your server, we can introspect some useful
information if the HTTP interface is enabled. Commands include:
    get vhost_names|channels|connections|queues

Usage: rabbit [options] command

Options:
  -h, --help            show this help message and exit
  -a SHTTPADDRESS, --address=SHTTPADDRESS
                        the TCP address of the HTTP rabbitmq_management
                        (default 127.0.0.1)
  -p IHTTPPORT, --port=IHTTPPORT
                        the TCP port of the HTTP rabbitmq_management plugin
                        (default 15672)

```
