# -*-mode: text; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-
# cucumber

  Feature: OTCmd2
  
    Settings for OTCmd2 are in a configobj .ini file that by default is
    found in the same place that the OTCmd2.py file is found, but you can
    use the OTCmd2.py '-c' or '--config' command-line option to specify
    an alternate location. It uses configobj with unrepr=True
    so the values are Python, not just strings.

  Scenario: Settings for OTCmd2 are in a configobj .ini file
  
      Given The configobj OTCmd2.ini exists
      And The configobj OTCmd2.ini is parseable
      And The configobj has keys:
                          OTCmd2
                          RabbitMQ
                          backtest
                          feed.plot.params
                          matplotlib.rcParams
      Then Life is Good!
