# -*-mode: text; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

@OTMql4AMQP @Mt4Running @Mt4Connected @examples
Feature: Send messages to a OTMql4AMQP enabled Mt4 about Account information.

  These tests will only work if you have an OTMql4AMQP enabled Metatrader running,
  the Experts/OTMql4/OTPyTestPikaEA.mq4 attached to a chart in it, and
  the RabbitMQ server configured and running.

  Scenario: OTCmd2-pub_wait-Accounts.txt

    Given Create the OTCmd2 instance
    Then  Collect share/examples to "RabbitMQ-pub_wait-Accounts.txt"
    
    Then  The "sub get" command will set the on-line target to be the default from OTCmd2.ini
    Then  The "sub set RabbitMQ" command will set the on-line target
    
    Then  The "sub run retval.# timer.#" command will give us a listener thread running, subscribed to retval.#
    
    Then  The "py import time" command will load the python time module
    Then  The "py time.sleep(15)" command will sleep for 15 seconds
    
    Then  The "chart list" command will get the list of charts we have seen because of listening to the timer
    Then  Assert type(self._G) == list and len(self._G) > 0
    Then  The "chart set" command will set the default chart to the first of list of charts we have seen
    Then  The "chart get" command will check the default chart 
    Then  Assert type(self._G) == str and len(self._G) > 0
    
    Then  The "pub set RabbitMQ" command will set the on-line speaker target
    
    Then  The "pub wait AccountBalance" command will wait for the retval from Mt4
    Then  Assert type(self._G) == float and type(self._G) > 0
    Then  The "pub wait AccountCompany" command will wait for the retval from Mt4
    Then  The "pub wait AccountCredit" command will wait for the retval from Mt4
    Then  Assert type(self._G) == float
    Then  The "pub wait AccountCurrency" command will wait for the retval from Mt4
    Then  Assert type(self._G) == str and len(self._G) >= 3
    Then  The "pub wait AccountEquity" command will wait for the retval from Mt4
    Then  Assert type(self._G) == float
    Then  The "pub wait AccountFreeMargin" command will wait for the retval from Mt4
    Then  Assert type(self._G) == float
    Then  The "pub wait AccountFreeMarginMode" command will wait for the retval from Mt4
    Then  Assert type(self._G) == float
    Then  The "pub wait AccountLeverage" command will wait for the retval from Mt4
    Then  Assert type(self._G) == int and self._G > 0
    Then  The "pub wait AccountMargin" command will wait for the retval from Mt4
    Then  Assert type(self._G) == float
    Then  The "pub wait AccountName" command will wait for the retval from Mt4
    Then  Assert type(self._G) == str and len(self._G) > 3
    Then  The "pub wait AccountNumber" command will wait for the retval from Mt4
    Then  Assert type(self._G) == int and self._G > 0
    Then  The "pub wait AccountProfit" command will wait for the retval from Mt4
    Then  Assert type(self._G) == float
    Then  The "pub wait AccountServer" command will wait for the retval from Mt4
    Then  Assert type(self._G) == str and len(self._G) > 3
    Then  The "pub wait AccountStopoutLevel" command will wait for the retval from Mt4
    Then  The "pub wait AccountStopoutMode" command will wait for the retval from Mt4
    Then  Write the share/examples file
    Then  Comment if you dont exit properly, the test will hang
    Then  Destroy the OTCmd2 instance
