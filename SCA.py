import sys
import time
from time import sleep

from cru_table import *

import ROC
from ROC import Roc

import UTILS
from UTILS import Utils

class Sca (Utils, Roc):
    def __init__(self, pcie_id, bar_ch, gbt_ch, board, debug = None):
        """
        Class constructor. Init the addresses and the file name
        """
        self.openROC(pcie_id, bar_ch, debug)      
        
        if board == 'CRU' : 
            self.base_add = CRUADD['add_gbt_sc']
        else :
            self.base_add = 0x30

        self.base_add = 0x0
	
	# set the channel
        self.rocWr(CRUADD['add_gbt_sc_link'], gbt_ch, debug)
        # Reset the CORE
        self.rocWr(CRUADD['add_gbt_sc_rst'], 0x1, debug)
        self.rocWr(CRUADD['add_gbt_sc_rst'], 0x0, debug)
        
        self.wr_add_data = CRUADD['add_gbt_sca{}_wr_data'.format(gbt_ch)]
        self.wr_add_cmd = CRUADD['add_gbt_sca{}_wr_cmd'.format(gbt_ch)]
        self.wr_add_ctr = CRUADD['add_gbt_sca{}_wr_ctr'.format(gbt_ch)]

        self.rd_add_data = CRUADD['add_gbt_sca{}_rd_data'.format(gbt_ch)]
        self.rd_add_cmd = CRUADD['add_gbt_sca{}_rd_cmd'.format(gbt_ch)]
        self.rd_add_ctr = CRUADD['add_gbt_sca{}_rd_ctr'.format(gbt_ch)]
        self.rd_add_mon = CRUADD['add_gbt_sca{}_rd_mon'.format(gbt_ch)]

        self.trid = 0x0
        self.cmd = 0x0
    #--------------------------------------------------------------------------------
    def wr(self, cmd, data, waitBusy, trid = None, debug = None):
        """
        Write the 64 bit (data + cmd)) to the SCA interface and execute the command
        If the TRID is not defined, it increments it for every wr
        waitBusy flag is used to execute the command without waiting the received feedback from the chip
        """
        if trid is None : 
            self.trid = self.trid + 1
            if (self.trid == 0xff):
                self.trid = 0x1
            self.cmd = cmd & 0xff00ffff
            self.cmd = self.cmd + (self.trid << 16)        
        else : 
            self.cmd = cmd & 0xff00ffff
            self.cmd = self.cmd + (trid << 16)        
        
        ret = 1
        while(ret == 1) :
            self.rocWr(self.wr_add_data, data, debug)
            self.rocWr(self.wr_add_cmd, self.cmd, debug)
            ret = self.exe(waitBusy, debug)
        
#        ret = 1
#        while(ret == 1) :
#            ret = self.checkTrid(trid)
        
        time = self.rocRd(self.rd_add_mon, debug)
        time = time & 0xffff
        print('WR - DATA %10s CH %4s TR %4s CMD %4s TIME %d' % (hex(data), hex(self.cmd >> 24),  hex((self.cmd >> 16) & 0xff), hex(self.cmd & 0xff), time))
    #--------------------------------------------------------------------------------

    def checkTrid(self, trid, debug = None) :  
        cmd = self.rocRd(self.rd_add_cmd, debug)
         
        tr_id = (cmd >> 16) & 0xff
        
#        print('%d -  %d' % (trid, tr_id))

        if tr_id == trid : 
            return 0 
        else : 
            return 1

    #--------------------------------------------------------------------------------
    def rd(self, debug = None) :
        """
        Read the feedback from the SCA component
        """
        err_cnt = 0
        err_int = 64
        while (err_int != 0) :
            data = self.rocRd(self.rd_add_data, debug)
            cmd = self.rocRd(self.rd_add_cmd, debug)
            ctrl = self.rocRd(self.rd_add_ctr, debug)

            err_code = hex(cmd & 0xff)    
            err_int = int(err_code,0)

            tr_id = (cmd >> 16) & 0xff
            if (tr_id == 0) :
                print('MAJOR ERROR ')
                return 1
        
            if err_int == 64 :
                # CH BUSY
                time.sleep(1.0/1000.0)
            elif err_int != 0 :
                # ERROR
                err_cnt += 1
                self.error(err_code)
                time.sleep(1.0/100.0)
                return 1
            else :
                print('RD - DATA %10s CH %4s TR %4s ERR %4s CTRL %4s' % (hex(data), hex(cmd >> 24), hex((cmd >> 16) & 0xff), hex(cmd & 0xff), hex(ctrl)))
            
            return 0
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------
    def exe(self, waitBusy, debug = None) :
        """
        Trigger the execution of the SCA command
        EXE function will wait for RX BUSY if waitBusy is 1 otherwise it will not wait for the core BUSY
        """
        self.rocWr(self.wr_add_ctr, 0x4, debug)
        self.rocWr(self.wr_add_ctr, 0x0, debug)
        if waitBusy == 1:
            ret = self.waitBusy(debug)
            return ret
        else :
            ret = self.waitTXBusy(debug)
            return ret
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------    
    def waitBusy(self,debug = None) :
        """
        Wait for the SCA component to be available
        """
        busy_cnt = 0
        busy = 0x1
        
        while (busy == 0x1) :
            busy = self.rocRd(self.rd_add_ctr, debug)
            busy = busy >> 31
            busy_cnt = busy_cnt + 1
            if busy_cnt == 1e6:
                return 1
                #print('CHIP is stuck ... exiting')
                #sys.exit()
            else :
                return 0
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------       
    def waitTXBusy(self,debug = None) :
        """
        Wait for the SCA component to complete the TX serialization
        """
        busy_cnt = 0
        busy = 0x1
        
        while (busy == 0x1) :
            busy = self.rocRd(self.rd_add_ctr, debug)
            # take only the bit[30]
            busy = (busy >> 30) & 0x1
            busy_cnt = busy_cnt + 1
            if busy_cnt == 1e6:
                return 1
            else :
                return 0
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------       
    def init(self, debug = None) :
        """
        Init the SCA communication
        """
        print ('SCA Reset')
        self.rocWr(self.wr_add_ctr, 0x1, debug)
        self.waitBusy(debug)
#        self.rd(debug)
        print ('SCA Init')
        self.rocWr(self.wr_add_ctr, 0x2, debug)
        self.waitBusy(debug)
#        self.rd(debug)
        
        self.rocWr(self.wr_add_ctr, 0x0, debug)
    #--------------------------------------------------------------------------------    

    #--------------------------------------------------------------------------------    
    def reset(self, debug = None) :
        """
        RESET the SCA block inside the FPGA
        """
        self.rocWr(self.wr_add_ctr, 0x800000, debug)
        self.rocWr(self.wr_add_ctr, 0x0, debug)
    #--------------------------------------------------------------------------------    
    
    #--------------------------------------------------------------------------------    
    def displayAdd(self) :
        """
        Function to print the BASE ADD
        """
        print('-------------------------------------------------------')
        print('SCA ADD:')
        print('BASE ADD = %s ' %(hex(self.base_add)))
        print('-------------------------------------------------------')
    #--------------------------------------------------------------------------------    
        
    #--------------------------------------------------------------------------------    
    def gpioEn(self, debug = None) :
        """
        Enable the GPIO
        """

        trid = None
        
        # Enable GPIO
        # WR CONTROL REG B
        self.wr(0x00010002, 0xff000000, 1, trid, debug)
        self.rd(debug)
        # RD CONTROL REG B
        self.wr(0x00020003, 0xff000000, 1, trid, debug)
        self.rd(debug)
        
        # WR GPIO DIR
        #scaWr(ch, 0x02030020, 0xffffffff)
        self.wr(0x02030020, 0xffc003ff, 1, trid, debug)
        self.rd(debug)
        # RD GPIO DIR
        self.wr(0x02040021, 0x0, 1, trid, debug)
        self.rd(debug)    
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------    
    def gpioWr(self, data, debug = None) :
        """
        Write 32 bit to the GPIO register
        """

        trid = None
        
        # WR REGISTER OUT DATA
        self.wr(0x02040010, data, 1, trid, debug)
        # RD DATA
        self.wr(0x02050011, 0x0, 1, trid, debug)
        self.rd(debug)
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------    
    def alfOPS(self, cmd, data, debug = None):
        """
        Function to access a GPIO register
        """
        trid = None
        # WR 
        self.wr(cmd, data, 1, trid, debug)
        self.rd()
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------    
    def gpioINTSEL(self, data):
        """
        Function to access a GPIO register
        """        
        # WR 
#        self.wr(02010030, data, 1)
        # RD
#        self.wr(02020031, 0x0, 1)
        rd(ch)
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------    
    def adcEn(self) :
        """
        Enable the ADC channel
        """
        # WR CONTROL REG D
#        self.wr(0x00010006, 0xff000000, 1)
        self.rd()
        # RD CONTROL REG B
#        self.wr(0x00020007, 0xff000000, 1)
        self.rd()
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------
    def scaID(self):
        """
        Report the SCA ID
        """
#        self.wr(0x14010091, 0x00000001, 1)
        self.rd()    
    #--------------------------------------------------------------------------------    

    #--------------------------------------------------------------------------------    
    def error(self, err_code):
        """
        Check the ERROR code returned by the SCA transaction
        """
        error_int = int(err_code,0)
        for i in range(0,8):
            error = error_int >> i
            error = error & 0x1
            
            if error == 1:
                if i == 0:
                    print('1 -> generic error flag')
                elif i == 1:
                    print('1 -> invalid channel request')
                elif i == 2:
                    print('1 -> invalid command request')
                elif i == 3:
                    print('1 -> invalid transactio number request')
                elif i == 4:
                    print('1 -> invalid length')
                elif i == 5:
                    print('1 -> channel not enabled')
                elif i == 7:
                    print('1 -> command in treatment')
                else:
                    print('0')
    #--------------------------------------------------------------------------------    

    #--------------------------------------------------------------------------------    
    def TpcCfgFile(self, file_name):
        """
        Update TPC config file name
        """
        if file_name == '':
            self.file_name = 'tpc_cmds'
        else :
            self.file_name = file_name
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------    
    def TPCEN(self, slow, debug = None):
        """
        TPC function to test the FEC configuration over SCA
        """
        line_num = 0    
        
        with open(self.file_name, 'r') as f:
            for line in f:
                line_num = line_num + 1
                if line[0] == '#':
                    print(line)
                    continue
                line = line.replace(',', '')
                l =  line.split()
                trid = l[9]
                chan = l[12]
                cmd = l[18]
                data = l[21]
                
                sca_chan = hex(int(chan))
                
                if sca_chan == '0x0' :
                    data = self.invertByte(data)
                if sca_chan == '0x2' and (cmd == '0x10' or cmd == '0x20'):
                    data = self.invertByte(data)
                if sca_chan == '0x3' and (cmd == '0x30'):
                    data = self.invertByte(data)
                if sca_chan == '0x4' and (cmd == '0x30' or cmd == '0xda' or cmd == '0x40' or cmd == '0x86'):
                    data = self.invertByte(data)
                if sca_chan == '0x7' and (cmd == '0x30'):
                    data = self.invertByte(data)
                if sca_chan == '0x8' and (cmd == '0x30'):
                    data = self.invertByte(data)
                if sca_chan == '0x9' and (cmd == '0x30'):
                    data = self.invertByte(data)
                if sca_chan == '0xa' and (cmd == '0x30'):
                    data = self.invertByte(data)
                if sca_chan == '0xb' and (cmd == '0x30'):
                    data = self.invertByte(data)
                if sca_chan == '0x14' and (cmd == '0x70'):
                    data = self.invertByte(data)
                
                sca_chan = format(int(chan),'02x')
                sca_trid = format(int(trid),'02x')
                sca_cmd = cmd.replace('0x', '')
            
                sca = '0x' + sca_chan + sca_trid + '00' + sca_cmd
                #sca = sca_chan + trid + '00' + sca_cmd
                sca_int = int(sca, 0)
                data_int = int(data, 0)
                #            print sca, data
                ret = 1
                while(ret == 1) :
                    self.wr(sca_int, data_int, 1, int(trid), debug)
                    if slow == 1: 
                        time.sleep(1.0)
                    ret = self.rd(debug)
    #--------------------------------------------------------------------------------    

    #--------------------------------------------------------------------------------    
    def MidCfgFile(self, file_name):
        """
        Update MID config file name
        """
        if file_name == '':
            self.file_name = 'mid_cmds'
        else :
            self.file_name = file_name
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------    
    def MIDEN(self, debug = None):
        """
        MID function to test the FEC configuration over SCA
        """
        line_num = 0
        
        with open(self.file_name, 'r') as f:
            for line in f:
                line_num = line_num + 1
                if line[0] == '#':
                    print(line)
                    continue
                l =  line.split(" ")
                sca = l[0]
                data = l[1]
                               
                sca_int = int(sca, 0)
                data_int = int(data, 0)
                trid = None
                self.wr(sca_int, data_int, 1, trid, debug)
                time.sleep(0.1)
                self.rd(debug)
    
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------    

    def MFTEN_load(self, debug = None):
        """
        MFT function to load and save the configuration of SCA
        """
        line_num = 0
        with open(self.file_name, 'r') as f:
                data_file = [l for l in (line.strip() for line in f) if l] # removes empty lines and \n 
        self.mat = [] # creating a table with n lines and 3 columns (sca, data, time) 
        for line in data_file: # loop over the lines of the .dcs file and saving its input in table
            line_num = line_num + 1
            if line[0] == '#':
                print(line)
                continue
            l =  line.split(" ")
            if (len(l)==2) : l.append('0')
            self.mat.append([int(x,0) for x in l[:-1]]+[float(l[-1])])
 
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------    
       
    def MFTEN_execute_cmd(self, debug = None):
        """
        MFT function to execute - wr and rd - what was loaded and saved in MFTEN_load
        """
        for i in range(len(self.mat)): # loop to send the previously saved sequence (mat) to execution
                    sca_int = self.mat[i][0] 
                    data_int = self.mat[i][1]
                    trid = None
                    ret = 1
                    while(ret == 1) :
                        self.wr(sca_int, data_int, 1, trid, debug)
                        time.sleep(self.mat[i][2])
                        ret = self.rd(debug)
        print("End of event")

    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------    
       
    def MFTEN_execute(self, debug = None, k=0):
        """
        MFT function to determine if the execution should be in a loop or not
        """
        if (int(k)==0) : 
            self.MFTEN_execute_cmd(debug) 
        else : 
            while (1) : 
                self.MFTEN_execute_cmd(debug) 

    #--------------------------------------------------------------------------------    

    #--------------------------------------------------------------------------------    
    def MchCfgFile(self, file_name):
        """
        Update MCH config file name
        """
        if file_name == '':
            self.file_name = 'mch_cmds'
        else :
            self.file_name = file_name
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------    
    def MCHEN(self, debug = None):
        """
        MCH function to test the FEC configuration over SCA
        """
        line_num = 0

        with open(self.file_name, 'r') as f:
            for line in f:
                line_num = line_num + 1
                if line[0] == '#':
                    print(line)
                    continue
                l =  line.split(" ")
                sca = l[0]
                data = l[1]

                data = self.invertByte(data)
                
                sca_int = int(sca, 0)
                data_int = int(data, 0)
                #print sca, data
                trid = None
                self.wr(sca_int, data_int, 1, trid, debug)
                self.rd(debug)                                      
                
    #--------------------------------------------------------------------------------    
