# -*-mode: text; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-
# cucumber

@rabbitctl @examples
Feature: OTCmd2-backtest_recipe

  These tests will only work if you have pyrabbit installed:
  http://pypi.python.org/pypi/pyrabbit
  and have the 'rabbitmq_management' plugin to rabbitmq enabled.
  See the OS command 'rabbitmq-plugins list' and make sure
  the 'rabbitmq_management' and 'rabbitmq_web_dispatch' plugins are enabled.
  You dont need to have a listener thread running.

  Scenario: OTCmd2-rabbit.txt

    Given Create the OTCmd2 instance
    Given Collect share/examples to "OTCmd2-rabbit.txt"
    Then  The "rabbit get vhost_names" command will list the vhost_names
    Then  Assert len(self._G) > 0
    Then  The "rabbit get channels" command will list the channels
    Then  Assert len(self._G) > 0
    Then  The "rabbit get connections" command will list the connections
    Then  Assert len(self._G) > 0
    Then  The "rabbit get queues" command will list the queues
    Then  Assert len(self._G) > 0
    Then  Write the share/examples file
    Then  Destroy the OTCmd2 instance
