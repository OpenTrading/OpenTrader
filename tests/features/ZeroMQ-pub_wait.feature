# -*-mode: text; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-
# cucumber

@OTMql4Zmq @Mt4Running @examples
Feature: Send messages to a OTMql4Zmq enabled Mt4 about the terminal.

  These tests will only work if you have an OTMql4Zmq enabled Metatrader running,
  the Experts/OTMql4/OTZmqCmdEA.mq4 attached to a chart in it.

  Scenario: OTCmd2-pub_wait.txt

    Given Create the OTCmd2 instance
    Then  Collect share/examples to "OTCmd2-pub_wait.txt"
    Then  The "sub get" command will get the on-line targets from OTCmd2.ini
    
    Then  The "sub set ZeroMQ" command will set the on-line listener target
    
    Then  The "sub run retval timer" command will We need a listener thread running, subscribed to retval
    
    Then  The "py import time" command will load the python time module
    Then  The "py time.sleep(15)" command will sleep for 15 seconds
    
    Then  The "chart list" command will get the list of charts we have seen because of listening to the timer
    Then  Assert type(self._G) == list and len(self._G) > 0
    Then  The "chart set" command will set the default chart to the first of list of charts we have seen
    Then  The "chart get" command will check the default chart 
    Then  Assert type(self._G) == str and len(self._G) > 0
    
    Then  The "pub set ZeroMQ" command will set the on-line speaker target
    
    Then  The "pub wait OrdersTotal" command will wait for the retval from Mt4
    Then  Assert type(self._G) == int and self._G >= 0
    Then  The "pub wait Period" command will wait for the retval from Mt4
    Then  Assert type(self._G) == int and self._G > 0
    Then  The "pub wait RefreshRates" command will wait for the retval from Mt4
    Then  Assert self._G == True
    Then  The "pub wait Symbol" command will wait for the retval from Mt4
    Then  Assert type(self._G) == str and len(self._G) >= 3
    Then  The "pub wait TerminalCompany" command will wait for the retval from Mt4
    Then  Assert type(self._G) == str and len(self._G) > 3
    Then  The "pub wait TerminalName" command will wait for the retval from Mt4
    Then  Assert type(self._G) == str and len(self._G) > 3
    Then  The "pub wait TerminalPath" command will wait for the retval from Mt4
    Then  Assert type(self._G) == str and len(self._G) > 3
    Then  The "pub wait WindowBarsPerChart" command will wait for the retval from Mt4
    Then  Assert type(self._G) == int and type(self._G) > 0
    Then  Comment ##? string -1 pub wait WindowFind" command will wait for the retval from Mt4
    Then  The "pub wait WindowFirstVisibleBar" command will wait for the retval from Mt4
    Then  Assert type(self._G) == int and type(self._G) > 0
    Then  Comment ##? void pub wait WindowRedraw
    Then  The "pub wait WindowsTotal" command will wait for the retval from Mt4
    Then  Assert type(self._G) == int and type(self._G) > 0
    
    Then  Write the share/examples file
    Then  Comment if you dont exit properly, the test will hang
    Then  Destroy the OTCmd2 instance
