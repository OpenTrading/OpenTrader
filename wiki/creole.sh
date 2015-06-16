#!/bin/sh

#  The calling of OTCmd2 may need to be customized for your setup.
if [ -z "$OTPYTHON_EXE" ] ; then
    export OTPYTHON_EXE="sh /c/bin/tpython.sh"
fi

if [ -z "$OTCMD2" ] ; then
    export OTCMD2="$OTPYTHON_EXE OpenTrader/OTCmd2.py"
fi

# We run these tests in this directory of the source distribution
if [ ! -f setup.py -o -f test.sh ] ; then
    cd ..
fi
if [ ! -f setup.py -o -f test.sh ] ; then
    echo "ERROR: We run this script in the root directory of the source distribution:"
    exit 7
fi

DOS="subscribe publish chart order csv backtest rabbit"

rm -f share/doc/1?OTCmd2_*  wiki/DocOTCmd2* wiki/_Sidebar.creole wiki/_Footer.creole

# _Sidebar.creole
echo '**Index**' > wiki/_Sidebar.creole
echo "* [[TitleIndex]]" >> wiki/_Sidebar.creole
echo -e '\n**OTCmd2 Manual**\n' >> wiki/_Sidebar.creole
echo "* [[DocOTCmd2]]" >> wiki/_Sidebar.creole
echo "* [[DocOTCmd2]]" >> wiki/_Sidebar.creole
$OTCMD2 -h | /g/Agile/bin/cmd2help_to_creole.sh \
	>> wiki/DocOTCmd2.creole

last=""
for elt in ${DOS} ; do
    echo "=== OTCmd2 $elt" > wiki/DocOTCmd2_$elt.creole
    $OTCMD2 help $elt | /g/Agile/bin/cmd2help_to_creole.sh \
	>> wiki/DocOTCmd2_$elt.creole
    echo -n "Next: [[DocOTCmd2_$elt]]" >> wiki/DocOTCmd2$last.creole
    echo "* [[DocOTCmd2_$elt]]" >> wiki/_Sidebar.creole
    echo wiki/DocOTCmd2_$elt.creole
    last="_$elt"
  done

# _Sidebar.creole
echo -e '\n**OTBackTest Manual**\n' >> wiki/_Sidebar.creole
echo "* [[DocOTBackTest]]" >> wiki/_Sidebar.creole
echo -e '\n**OTPpnAmgc Manual**\n' >> wiki/_Sidebar.creole
echo "* [[DocOTPpnAmgc]]" >> wiki/_Sidebar.creole

# _Footer.creole
echo -n "Home: [[Home]] " > wiki/_Footer.creole
echo -n " Index: [[TitleIndex]] " >> wiki/_Footer.creole
