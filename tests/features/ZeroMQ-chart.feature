# -*-mode: text; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-
# cucumber

@OTMql4Zmq @Mt4Running  @Mt4Connected @examples
Feature: Send messages to a OTMql4Zmq enabled Mt4 about charts

  These tests will only work if you have an OTMql4Zmq enabled Metatrader running,
  the Experts/OTMql4/OTZmqCmdEA.mq4 attached to a chart in it.
  AND the Mt4 is logged in and connected.
  
  Scenario: OTCmd2-chart.txt

    Given Create the OTCmd2 instance
    Given Collect share/examples to "OTCmd2-chart.txt"

    Then  The "sub get" command will set the on-line target to be the default from OTCmd2.ini
    Then  The "sub set ZeroMQ" command will set the on-line target for listening
    
    Then  The "sub run retval.# timer.#" command will start a listener thread running, subscribed to retval and timer topics
    
    Then  The "py import time" command will load the python time module
    Then  The "py time.sleep(15)" command will sleep for 15 seconds
    
    Then  The "chart list" command will list all the charts the listener has heard of
    Then  The "chart set" command will set the target chart to the last one weve seen
    Then  The "chart get" command will show the target chart we have set
    
    Then  Write the share/examples file
    Then  Comment if you dont exit properly, the test will hang
    Then  Destroy the OTCmd2 instance
