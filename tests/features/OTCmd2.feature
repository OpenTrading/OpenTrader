# -*-mode: text; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-
# cucumber

@pytest
Feature: OTCmd2

  You dont need to have a listener thread running.

  Scenario: Load OTCmd2

    Given Create the OTCmd2 instance
    Then  The "help" command output contains "Documented commands"
    Then  The "garbage" command error contains "ERR:"
    Then  Destroy the OTCmd2 instance

