#!/usr/bin/env python3.8

import sys
import argparse
import SCA 
from SCA import Sca
import multiprocessing
import time
from tkinter import *
from multiprocessing import shared_memory
import ctypes
import numpy as np
import guiapp

def main():

    file_name = 'Setup0_Config.dat'
    line_num = 0
    Arg=[]
    with open(file_name, 'r') as f:
        data_file = [l for l in (line.strip() for line in f) if l]
    for line in data_file:
        if line[0] == '#':
            print(line)
            continue
        l =  line.split(" ")
        Arg.append(l[1])
        line_num = line_num + 1

    id_card = Arg[0]
    board = Arg[1]
    gbt_ch = int(Arg[2])
    debug = None
    print(id_card,board,gbt_ch)
    dcsConfigName= 'ConfigD0'
    dcsSeqName= 'MonitorD0'

    sca = Sca(id_card, 2, gbt_ch, board, debug)
    sca.displayAdd()
    print ( "-----------------> Execute" + dcsSeqName )

    return sca, id_card, gbt_ch, board, debug
 

def GBT_SCA(D, mat0, sca, dat, En_DCDC_bool, RE):

    existing_shm1=shared_memory.SharedMemory(name='SM1')
    sq0=np.ndarray(mat0.shape, dtype=mat0.dtype, buffer=existing_shm1.buf)

    existing_shm2=shared_memory.SharedMemory(name='SM2')
    B=np.ndarray(D.shape, dtype=D.dtype, buffer=existing_shm2.buf)

    existing_shm3=shared_memory.SharedMemory(name='SM3')
    data0=np.ndarray(dat.shape, dtype=dat.dtype, buffer=existing_shm3.buf)

    existing_shm4=shared_memory.SharedMemory(name='SM4')
    En_DCDC=np.ndarray(En_DCDC_bool.shape, dtype=En_DCDC_bool.dtype, buffer=existing_shm4.buf) 

    existing_shm5=shared_memory.SharedMemory(name='SM5')
    RE_adress=np.ndarray(RE.shape, dtype=RE.dtype, buffer=existing_shm5.buf) 

    A=[[0,0,0]]
    DCDC=[0,0]
    set_add=int('0x020b0010',16)

    GPIO=[0,0,0,0,0,0,0,0]
    h=0
    for i in range(len(sq0)):
        if(sq0[i][0]==set_add):
            print(sq0[i][1])
            GPIO[h]=sq0[i][1]
            h=h+1

    print(GPIO)

    while(True): 
        for i in range(len(B)):
            if (B[i]):
                dcsConfigName= 'ConfigD{}'.format(i)
                sca.MidCfgFile(dcsConfigName)
                sca.MFTEN_load(debug)
                sca.MFTEN_execute_cmd(debug)
                while (B[i]):
                    sca.MFTEN_execute_cmd(debug, sq0.tolist())
                    data0[:]=np.array(sca.data)[:]
                    for j in range(len(En_DCDC)):
                        if (En_DCDC[j]):
                            DCDC[j] = 1 - DCDC[j]
                            if DCDC[j]==1:                          
                                print("INSIDE ENABLE DCDC")
                            else :
                                print("INSIDE DISABLE DCDC")
                            En_DCDC[j]=False
                        EN_adress = (DCDC[1]<<9) + (DCDC[0]<<8)
                    o=0
                    for k in range(len(sq0)):
                        if (sq0[k][0]==set_add): 
                            sq0[k][1]=GPIO[o]+EN_adress+RE_adress[0]
                            o=o+1
                print(sq0)
                print("##############################################")            
                print(data0)

    del sq0
    existing_shm1.close()
    del B
    existing_shm2.close()
    del data0
    existing_shm3.close()

if __name__ == '__main__' :

    sca0, id_card, gbt_ch, board, debug = main()

    root = Tk()
    root.geometry('500x1000')
    root.title("Monitoring GUI")
    gui = guiapp.GuiApp(master=root)

    D_bool=np.array([False]*5)
    shm2= shared_memory.SharedMemory(name='SM2', create=True, size=D_bool.nbytes)
    D=np.ndarray(D_bool.shape, dtype=D_bool.dtype, buffer=shm2.buf)
    D[:]=D_bool[:]

    dcsConfigName= 'ConfigD0'
    sca0.MidCfgFile(dcsConfigName)
    sca0.MFTEN_load(debug)
    sca0.MFTEN_execute_cmd(debug)
 
    dcsSeqNameD0= 'MonitorD0'
    sca0.MidCfgFile(dcsSeqNameD0)
    sca0.MFTEN_load(debug)
    sq0=np.array(sca0.mat)
    sca0.MFTEN_execute_cmd(debug, sq0.tolist())
    dat=np.array(sca0.data)
    
    shm1= shared_memory.SharedMemory(name='SM1', create=True, size=sq0.nbytes)
    mat0=np.ndarray(sq0.shape, dtype=sq0.dtype, buffer=shm1.buf) 
    mat0[:]=sq0[:]

    shm3= shared_memory.SharedMemory(name='SM3', create=True, size=dat.nbytes)
    data0=np.ndarray(dat.shape, dtype=dat.dtype, buffer=shm3.buf) 
    data0[:]=dat[:]
    
    En_DCDC_bool=np.array([False]*2)
    shm4= shared_memory.SharedMemory(name='SM4', create=True, size=En_DCDC_bool.nbytes)
    En_DCDC=np.ndarray(En_DCDC_bool.shape, dtype=En_DCDC_bool.dtype, buffer=shm4.buf)
    En_DCDC[:]=En_DCDC_bool[:]

    RE_=np.array([0])
    shm5= shared_memory.SharedMemory(name='SM5', create=True, size=RE_.nbytes)
    RE=np.ndarray(RE_.shape, dtype=RE_.dtype, buffer=shm5.buf)
    RE[:]=RE_[:]

    t1=multiprocessing.Process(target=gui.MainFunc, args=(D, mat0, data0, En_DCDC, RE, root,))
    t1.start()
    t2=multiprocessing.Process(target=GBT_SCA, args=(D, mat0, sca0, data0, En_DCDC, RE,))
    t2.start()

    t1.join()
    t2.join()

    del mat0
    shm1.close()
    shm1.unlink()  
    del D
    shm2.close()
    shm2.unlink()
    del data0
    shm3.close()
    shm3.unlink()

    root.destroy()

