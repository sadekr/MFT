#!/usr/bin/env python

import sys
import argparse

import SCA 
from SCA import Sca

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id", required=True, help="card ID")
    parser.add_argument("-b", "--board", default="CRU", help="card type CRU/GRORC")
    parser.add_argument("-l", "--links", type=int, default=0, help="specifiy link ID")
    parser.add_argument("-f", "--file", default="", help="Specify dcs file name")
    parser.add_argument("-k", "--cond", default=0, help="loop over a sequence") 
    args = parser.parse_args()
        
    id_card = args.id
    gbt_ch = args.links
    board = args.board
    debug = None
    k=args.cond

    if args.file == "":
        dcsFileName = "all_s.dcs"
    else:
        dcsFileName= args.file
	
    sca = Sca(id_card, 2, gbt_ch, board, debug)
    sca.displayAdd()

    print ( "-----------------> Execute" + dcsFileName )
    if gbt_ch == 0:
        dcsLogFileName = dcsFileName + "-logl0"
    else:
        dcsLogFileName = dcsFileName + "-logl1"
    dcsLogFile = open(dcsLogFileName, 'w')
    stdoutBackup = sys.stdout
    #sys.stdout = dcsLogFile
    
    sca.MidCfgFile(dcsFileName)
    sca.MFTEN_load(debug)
    sca.MFTEN_execute(debug, k)
    #dcsLogFile.close()
    sys.stdout = stdoutBackup

if __name__ == '__main__' :
    main()
