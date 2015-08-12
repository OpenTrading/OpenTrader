# -*-mode: text; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-
# cucumber

@OTMql4Zmq @Mt4Running @examples
Feature: Send messages to a OTMql4Zmq enabled Mt4 about orders

  These tests will only work if you have an OTMql4Zmq enabled Metatrader running,
  the Experts/OTMql4/OTZmqCmdEA.mq4 attached to a chart in it.

  Scenario: OTCmd2-ord.txt

    Given Create the OTCmd2 instance
    Given Collect share/examples to "OTCmd2-ord.txt"
    Then  The "sub get" command will set the on-line target to be the default from OTCmd2.ini
    Then  The "sub set ZeroMQ" command will set the on-line target for listening
    
    Then  The "sub run retval timer" command will start a listener thread running, subscribed to retval and timer topics
    
    Then  The "py import time" command will load the python time module
    Then  The "py time.sleep(15)" command will sleep for 15 seconds
    
    Then  The "chart set" command will set the target chart to the last one weve seen
    Then  The "pub set ZeroMQ" command will set the on-line target for speaking
    
    Then  The "order list" command will list the details of current orders
    Then  The "order history" command will list the details of closed orders
    
    Then  Write the share/examples file
    Then  Comment if you dont exit properly, the test will hang
    Then  Destroy the OTCmd2 instance
