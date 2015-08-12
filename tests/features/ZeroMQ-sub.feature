# -*-mode: text; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-
# cucumber

@OTMql4Zmq @Mt4Running @examples
Feature: Subscribe to messages from ZeroMQ on a given topic

  These tests will only work if you have an OTMql4Zmq enabled Metatrader running,
  the Experts/OTMql4/OTZmqCmdEA.mq4 attached to a chart in it.

  Scenario: OTCmd2-sub.txt

    Given Create the OTCmd2 instance
    Given Collect share/examples to "OTCmd2-sub.txt"
    Then  The "sub get" command will set the on-line target to be the default from OTCmd2.ini
    Then  The "sub set ZeroMQ" command will set the on-line target
    Then  The "sub run retval.# timer.#" command will start a listener thread running, subscribed to retval and timer topics
    Then  The "py import time" command will load the python time module
    Then  The "py time.sleep(15)" command will sleep for 15 seconds
    Then  The "sub show" command will list the message topics that are being hidden
    Then  The "py time.sleep(15)" command will you should see some timer messages in JSON format
    Then  The "sub hide timer" command will stop seeing timer messages
    Then  The "py time.sleep(15)" command will now you should see no timer messages
    Then  The "sub show timer" command will start seeing timer messages again
    Then  The "py time.sleep(15)" command will now you should see timer messages
    Then  The "sub pprint" command will show TOPIC messages with pretty-printing
    Then  The "sub pprint 0" command will set pretty printing: with 0 - off, 1 - on
    Then  The "sub pprint 1" command will show pretty printing current value with no argument
    Then  The "sub thread info" command will info on the thread listening for messages.
    Then  The "sub thread enumerate" command will enumerate all threads
    Then  Write the share/examples file
    Then  Destroy the OTCmd2 instance
