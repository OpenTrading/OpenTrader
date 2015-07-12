# -*-mode: text; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-
# cucumber

@pytest @pybacktest @examples
Feature: OTCmd2-backtest_recipe

  Scenario: OTCmd2-backtest_recipe.txt

    Given Create the OTCmd2 instance
    Given Collect share/examples to "OTCmd2-backtest_recipe.txt"
    Then  The "back recipe list" command will list the known recipes
    Then  The result will be a not-null list
    Then  The "back recipe set" command will show the current recipe
    Then  The result will be a not-null list
    Then  The "back recipe set SMARecipe" command will set the current recipe
    Then  The result will be a not-null string
    Then  The "back recipe config" command will show the current recipe config
    Then  The result will be a not-null list

    Then  The "back recipe config default" command will show the current recipe config default section
    Then  Assert len(self._G) > 0
    Then  Assert len(self._G.keys()) > 0
    Then  Assert 'sName' in self._G
    Then  Assert 'sDescription' in self._G
    Then  Assert 'fRecipeVersion' in self._G
    Then  Assert 'lRequiredFeedParams' in self._G
    Then  Assert 'lRequiredDishesParams' in self._G
    Then  Assert 'lRequiredIngredientsParams' in self._G
    Then  The "back recipe config" command will show the current recipe config sections
    Then  Assert len(self._G) > 0
    Then  Assert 'mFeedOhlc' in self._G
    Then  Assert 'rShortMa' in self._G
    Then  Assert 'rLongMa' in self._G
    Then  Write the share/examples file
    Then  Destroy the OTCmd2 instance
