# -*-mode: text; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-
# cucumber

@pytest @pybacktest @examples
Feature: OTCmd2-backtest_omlette

  These tests will only work if you have pybacktest installed:
  https://github.com/ematvey/pybacktest
  You dont need to have a listener thread running.

  Scenario: OTCmd2-backtest_omlette.txt

    These tests will only work if you have created a CSV file tmp/EURUSD60-2014.csv

    Given Create the OTCmd2 instance
    Given Collect share/examples to "OTCmd2-backtest_omlette.txt"

    When  Assert os.path.exists("tmp/EURUSD60-2014.csv")

    Then  The "back omlette open tmp/EURUSD60-2014.hdf" command will save the results of this backtest
    Then  The "back omlette check" command will check that the omlette HDF5 file is valid

    Then  The "back feed read_mt4_csv tmp/EURUSD60-2014.csv EURUSD 60 2014" command will read a CSV file from Mt4
    Then  The "back feed list" command will list the feeds we have read

    Then  The "back recipe list" command will list the known recipes
    Then  The "back recipe set SMARecipe" command will set the current recipe
    Then  The "back recipe config" command will show the current recipe config

    Then  The "back chef list" command will list the known chefs
    Then  The "back chef set PybacktestChef" command will set the current chef
    Then  The "back recipe ingredients" command will make the ingredients
    Then  The "back chef cook" command will cook the recipe by the chef

    Then  Comment This should be done in this order:
    Then  The "back servings list" command will show the list of servings
    Then  The "back servings signals" command will show the signals
    Then  The "back servings trades" command will show the trades
    Then  The "back servings positions" command will show the positions
    Then  The "back servings equity" command will show the equity
    Then  The "back servings trade_price" command will show the trade_price
    Then  The "back servings reviews" command will show the reviews

    Then  The "back omlette display" command will display gives a complete listing of the contents of the HDF file
    Then  The "back omlette close" command will close and save the HDF file
    Then  Assert os.path.isfile('tmp/EURUSD60-2014.hdf')
    Then  Write the share/examples file
    Then  Destroy the OTCmd2 instance
