#!/bin/bash 

if [ -z $1 ]
then
        echo "The script needs of Link number and DCS file name."
        return
else
        link=$1
fi

if [ -z $2 ]
then
        echo "The script needs of Link number and DCS file name."
        return
else
        dcsFile="/home/flp/mft/$2"
        dcsLog="$dcsFile-logl$link"
fi

#cd /home/flp/cru-sw/GBTSC/sw

python sca_config.py -i03:00.0 -l$link -bCRU -f$dcsFile

if [ ! -z $3 ]
then 
        dcsFile="/home/flp/mft/$3"
        dcsLog="$dcsFile-logl$link"  
	#cd /home/flp/cru-sw/GBTSC/sw
	python sca_config.py -i03:00.0 -l$link -bCRU -f$dcsFile -k$4
fi

echo "----------------------- Dump of date registers ---------------------------"
grep -B1 'status : I2C' $dcsLog | grep -v 'Read'
echo "----------------------- Dump of config registers -------------------------"
grep -B1 'config :I2C' $dcsLog | grep -v 'Read'

#cd /home/mid/readout/sw/mid-daq
