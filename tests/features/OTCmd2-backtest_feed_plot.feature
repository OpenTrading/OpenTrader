# -*-mode: text; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-
# cucumber

@matplotlib @examples
Feature: Load a feed from a CSV file and plot the chart of data

  These tests require matplotlib be installed in your Python, 
  AND REQUIRE HUMAN INTERACTION to close the plot once it is displayed.
  These tests will only work if you have pybacktest installed:
  https://github.com/ematvey/pybacktest
  You dont need to have a listener thread running.

  Scenario: OTCmd2-backtest_feed_plot.txt

    These tests will only work if you have created a CSV file tmp/EURUSD60-2014.csv

    Given Create the OTCmd2 instance
    Given Collect share/examples to "OTCmd2-backtest_feed_plot.txt"
    Then  The "back recipe list" command will list the known recipes
    Then  The "back feed read_mt4_csv tmp/EURUSD60-2014.csv EURUSD 60 2014" command will read the feed CSV data
    Then  The "back feed info" command will show info about the feed
    Then  The "back feed plot" command will plot the data using matplotlib
    Then  Write the share/examples file
    Then  Destroy the OTCmd2 instance
