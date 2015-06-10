
These example files are OTCmd2 command scripts that you
can run from the command line with the stdin from these files.

For example, under Msys or Unix this would be:
```
OTCmd2 -P '/c/Program Files/MetaTrader'  < tests/OTCmd2-0.test
```

You should see no assertion errors,  and you should see no timeouts.
```
WARN: No retval returned in 60 seconds
```

You can adjust the timeout in the `[OTCmd2]` section of the
`OTCmd2.ini` config file with the value `iRetvalTimeout`.

