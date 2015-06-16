#!/bin/sh

# We run these tests in this directory of the source distribution
if [ ! -f setup.py -o -f test.sh ] ; then
    cd ..
fi
if [ ! -f setup.py -o -f test.sh ] ; then
    echo "ERROR: We run this script in the root directory of the source distribution:"
    exit 7
fi

GIT_USER=OpenTrading
PROJ=OpenTrader
DIR=OpenTrader
EX_URL="https://github.com/${GIT_USER}/${PROJ}/raw/master"

OUT="wiki/TestsFeatures.creole"
cp tests/Readme.creole $OUT
echo "" >> $OUT
for file in tests/features/*feature ; do \
    base=`basename $file .feature`
    echo "" >> $OUT
    echo "=== $base" >> $OUT
    echo "" >> $OUT
    echo "**[[$base.txt|${EX_URL}/$file]]**" >> $OUT
    #    grep '^    [a-zA-Z]' $file  >> $OUT
    grep -v '^#' $file | \
    sed -e 's@^ *Feature:@**Feature:**@' \
	-e 's@^ *Scenario: *\(.*\)@**Scenario:** \1\n{{{@' \
	>> $OUT
    echo '}}}'  >> $OUT
done
