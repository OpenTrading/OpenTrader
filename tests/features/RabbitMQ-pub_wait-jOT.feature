# cucumber" command will -*-mode: text; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

@OTMql4AMQP @Mt4Running @Mt4Connected @examples
Feature: Send messages to a OTMql4AMQP enabled Mt4 about JSON account information.

  These tests will only work if you have an OTMql4AMQP enabled Metatrader running,
  the Experts/OTMql4/OTPyTestPikaEA.mq4 attached to a chart in it, and
  the RabbitMQ server configured and running.

  Scenario: OTCmd2-pub_wait-jOT.txt

    Given Create the OTCmd2 instance
    Then  Collect share/examples to "RabbitMQ-pub_wait-jOT.txt"
    
    Then  The "sub get" command will show the on-line targets from OTCmd2.ini
    Then  The "sub set RabbitMQ" command will set the on-line target
    
    Then  The "sub run retval.# timer.#" command will We need a listener thread running, subscribed to retval.#
    
    Then  The "py import time" command will load the python time module
    Then  The "py time.sleep(15)" command will sleep for 15 seconds
    
    Then  The "chart list" command will get the list of charts we have seen because of listening to the timer
    Then  Assert type(self._G) == list and len(self._G) > 0
    Then  The "chart set" command will set the default chart to the first of list of charts we have seen
    Then  The "chart get" command will check the default chart 
    Then  Assert type(self._G) == str and len(self._G) > 0
    
    Then  The "pub set RabbitMQ" command will set the on-line speaker target
    
    Then  The "pub wait jOTAccountInformation" command will wait for the retval from Mt4
    Then  The "pub wait jOTOrdersTickets" command will wait for the retval from Mt4
    Then  The "pub wait jOTOrdersHistory" command will wait for the retval from Mt4
    Then  The "pub wait jOTOrdersTrades" command will wait for the retval from Mt4
    Then  Write the share/examples file
    Then  Comment if you dont exit properly, the test will hang
    Then  Destroy the OTCmd2 instance
