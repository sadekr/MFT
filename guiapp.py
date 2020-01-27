#!/usr/bin/env python3.8

import sys
from tkinter import *
from multiprocessing import Queue
import multiprocessing
from multiprocessing import shared_memory
import ctypes
import time
import numpy as np
import fileinput

class GuiApp(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()

    def start(self, disk, B, sq0, data0, zone, DACentry0, ADCentry0, ADCentry1, ADCentry2, ADCentry3, ADC0, ADC1, ADC2, ADC3):
        if (B[disk]==True):
            print("STOP")
            B[disk]=False
        else: 
            B[disk]=True
            self.ReadData( disk, B, sq0, data0, zone, DACentry0, ADCentry0, ADCentry1, ADCentry2, ADCentry3, ADC0, ADC1, ADC2, ADC3)

    def enDC(self, En_DCDC, i): # to change colors when EN: green / DIS: red
        print("In DCDC")
        En_DCDC[i]=True

    def clear(self, var): #not working
        for i in range(len(var)):
            var[i].set(0)

    def reset(self, var, RE_adress):

        va=[0,0,0,0]
        RE_ad=0

        for i in range(len(va)):
            if var[i] is None:
                va[i]=0
            else: 
                va[i]=var[i].get()
        print("###########")
        print(va)

        for j in range(len(va)):

            RE_ad = RE_ad + (va[j]<<j)

        RE_ad=[RE_ad]
        print(RE_ad,RE_adress)

        RE_adress[:]=RE_ad[:]

        time.sleep(2)
        RE_ad=0
        RE_adress[:]=np.array([0])[:]

    def ReadData(self, disk, B, sq0, data0, zone, DACentry0, ADCentry0, ADCentry1, ADCentry2, ADCentry3, ADC0, ADC1, ADC2, ADC3):

        if (B[disk]==True):
            A='0x150e0010'
            A=int(A,16)
            b='0x140b0030'
            b=int(b,16)
            j=0

            for i in range(len(sq0)):
                if (sq0[i][0] == A):
                    DACentry0[j].delete("1.0","end")
                    DACentry0[j].insert(END,data0[i+1]) #oblige de mettre sca pour update data selon sq. A optimiser
                    j=j+1
                    continue
                if (sq0[i][0] == b):
                    for h in range(len(ADCentry0)):
                        SQ=hex(int(sq0[i][1]))
                        if (hex(int(ADC0[h][1]))==SQ):
                            ADCentry0[h].delete("1.0","end")
                            ADCentry0[h].insert(END, data0[i+2])
                            break
                        if (hex(int(ADC1[h][1]))==SQ):
                            ADCentry1[h].delete("1.0","end")
                            ADCentry1[h].insert(END, data0[i+2])
                            break
                        if (hex(int(ADC2[h][1]))==SQ):
                            ADCentry2[h].delete("1.0","end")
                            ADCentry2[h].insert(END, data0[i+2])
                            break
                        if (hex(int(ADC3[h][1]))==SQ):
                            ADCentry3[h].delete("1.0","end")
                            ADCentry3[h].insert(END, data0[i+2])
                            break
        #print("IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
        #print(data0,sq0)
        self.after(3000, lambda : self.ReadData(disk, B, sq0, data0, zone, DACentry0, ADCentry0, ADCentry1, ADCentry2, ADCentry3, ADC0, ADC1, ADC2, ADC3))

    def set(self, DACentry, DACset, j, sq0, data0):

        print("in set-----------------------------------------")
        #print(data0)
        A='0x150e0010'
        A=int(A,16)
        J=0
        for i in range(len(sq0)):
            if (sq0[i][0]==A) : 
                print("In first cond OK")
                J=J+1
                h=i
            if (j+1==J) : 
                print("In second cond OK")
                sq0[h][1] = int(DACset.get(),16)
                DACentry.delete("1.0","end")
                DACentry.insert(END,hex(int(sq0[h][1]))) 
                DACset.delete(0,'end')
                break
        #print(data0) #pas de changement alors que c"est changé dans GBT-SCA

    def CreateZone(self, zone, x, y, sq0, root, data0):

        y1=y+10
        y2=y+120     

        DACentry=[]
        DACset=[]

        if (zone==0):
            label1= Label(root, text="DAC values:", width=12 ,font=("bold", 12))
            label1.place(x=x, y=y) 

            label2= Label(root, text="ADC values:", width=12 ,font=("bold", 12))
            label2.place(x=x, y=y+100) 

            DAC=["U_BB","Th_BB","Th_D","Th_A"]

            for i in DAC:
                y=y+20

                DAC0= Label(root, text= i, width=11 ,font=("bold", 11))
                DAC0.place(x=x, y=y) 
                DAC0entry=Text(root, height=1, width= 10)
                DAC0entry.place(x=x+75, y=y)
                DACentry.append(DAC0entry) 

                DAC0set=Entry(root, width="10")
                DAC0set.place(x=x+225,y=y)
                DACset.append(DAC0set)

            Button0=Button(root, text="Set:", command = lambda : self.set(DACentry[0], DACset[0], 0, sq0, data0), height = 1)
            Button0.place(x=x+165, y=y1)
            y1=y1+25
            Button1=Button(root, text="Set:", command = lambda : self.set(DACentry[1], DACset[1], 1, sq0, data0), height = 1)
            Button1.place(x=x+165, y=y1)
            y1=y1+25
            Button2=Button(root, text="Set:", command = lambda : self.set(DACentry[2], DACset[2], 2, sq0, data0), height = 1)
            Button2.place(x=x+165, y=y1)
            y1=y1+25
            Button3=Button(root, text="Set:", command = lambda : self.set(DACentry[3], DACset[3], 3, sq0, data0), height = 1)
            Button3.place(x=x+165, y=y1)

        return DACentry, DACset

    def CreateADC(self, zone, x, y, root): 
        label3= Label(root, text="ZONE {}:".format(zone), width=10 ,font=("bold", 10))
        label3.place(x=x, y=y+120) 

        file_name = 'GBT_SCA_PinOut_0.data'
        line_num = 0
        PinOut=[]
        with open(file_name, 'r') as f:
            data_file = [l for l in (line.strip() for line in f) if l]
        for line in data_file:
            if line[0] == '#':
                print(line)
                continue
            l =  line.split(" ")
            PinOut.append(l)
            line_num = line_num + 1

        ADC=[]
        ADCentry=[]
        y2=y+120 

        for j in range(len(PinOut)): 
            if 'ZONE{}'.format(zone) in PinOut[j][1]:
                ADC.append([PinOut[j][0] ,PinOut[j][2]])           

        for j in range(len(ADC)):
            y2=y2+20
            ADC0= Label(root, text= ADC[j][0], width=11 ,font=("bold", 11))
            ADC0.place(x=x, y=y2) 
            ADC0entry=Text(root, height=1, width= 10)
            ADC0entry.place(x=x+75, y=y2)
            ADCentry.append(ADC0entry)

        return ADC, ADCentry


    def MainFunc(self, D, mat0, dat, En_DCDC_bool, RE, root):
        print("in mf")
        label0= Label(root, text="D0:", width=15 ,font=("bold", 15))
        label0.place(x=15, y=10) 
        zone=0
        x=15
        y=40
        print("Phase 1")

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

        DACentry0, DACset0 = self.CreateZone(zone, x, y, sq0, root, data0)

        ADC0, ADCentry0 = self.CreateADC(zone, x, y, root)      
        ADC1, ADCentry1 = self.CreateADC(1,170,40,root)
        ADC2, ADCentry2 = self.CreateADC(2,15,240,root)
        ADC3, ADCentry3 = self.CreateADC(3,170,240,root)
        print("Phase2")
        disk=0
        button0=Button(root, text="START/STOP", command = lambda : self.start(disk, B, sq0, data0, zone, DACentry0, ADCentry0, ADCentry1, ADCentry2, ADCentry3, ADC0, ADC1, ADC2, ADC3))
        button0.place(x=150, y=10)

        button1=Button(root, text="Enable/Disable DCDC", command = lambda : self.enDC(En_DCDC, 1))
        button1.place(x=120, y=320)
 
        button2=Button(root, text="Enable/Disable DCDC", command = lambda : self.enDC(En_DCDC, 0))
        button2.place(x=120, y=520)
 
        label1= Label(root, text="_________________________", font=("bold", 20))
        label1.place(x=15, y=550)
        label1.configure(foreground="white")

        label2= Label(root, text="__________________________", height = 1 ,font=("bold", 20))
        label2.place(x=15, y=640)
        label2.configure(foreground="white")


        var=[None]*4
        for i in range(len(var)):
            var[i]=IntVar()

        Radiobutton(root, text="ZONE0", variable=var[3], value=1).place(x=15,y=600)
        Radiobutton(root, text="ZONE2", variable=var[0], value=1).place(x=15,y=630)
        Radiobutton(root, text="ZONE1", variable=var[2], value=1).place(x=140,y=600)
        Radiobutton(root, text="ZONE3", variable=var[1], value=1).place(x=140,y=630)

        button3=Button(root, text= "RESET", command = lambda : self.reset(var, RE_adress))
        button3.place(x=250, y=590)

        button4=Button(root, text= "CLEAR", command = lambda : self.clear(var))
        button4.place(x=250, y=630)


        print("phase 3")
        self.mainloop()

        print("GOOD BYE")
        print(data0) 

        del sq0, B, data0 
        existing_shm1.close()
        existing_shm2.close()
        existing_shm3.close()

