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

class GuiApp(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)                                                                
        self.pack()

    def print_contents(self, event):
        print("Entry content is: ", \
              self.contents.get())

    def read_value(self, mat):
        print(mat.shape)
        label = Label(root, text= mat[1][0], width=20, font=("bold",10))
        label.place(x=70,y=130)

    def read_value1(self, mat):
        label = Label(root, text= mat[1][2], width=20, font=("bold",10))
        label.place(x=70,y=200)
    
    def change_value(self, mat, sq):
        mat[1][0] = 55555
        print(mat[1][0],sq[1][0])
        print(mat,sq)

    def createWidgets(self, sq):                                      
        print(" In createWidgers ")
        QUIT = Button(self, fg= "red", text = "Q", command = self.quit)
        QUIT.pack(side = "right")                               
        self.entrythingy = Entry()
        self.entrythingy.pack()
        self.contents = StringVar()
        self.contents.set("Enter variable")                                                      
        self.entrythingy["textvariable"] = self.contents
        self.entrythingy.bind('<Key-Return>',
                              self.print_contents)

        existing_shm=shared_memory.SharedMemory(name='SM1')
        mat=np.ndarray(sq.shape, dtype=sq.dtype, buffer=existing_shm.buf)
 
        button1=Button(self, text=" Value of mat[1][0] ", command = lambda : self.read_value(mat))
        button1.pack()
        button3=Button(self, text=" Value of mat[1][2] ", command = lambda : self.read_value1(mat))
        button3.pack()
        button2=Button(self, text=" Change mat[1][0] ", command = lambda : self.change_value(mat,sq))
        button2.pack()
        self.mainloop()

        del mat
        existing_shm.close()


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
    mat=sca.MFTEN_load(debug)
    sca.MFTEN_execute_cmd(debug, mat)
    global h
    if k==1 :
        h=True
    #dcsLogFile.close()
    sys.stdout = stdoutBackup

def sequence_loop(sq):
    existing_shm=shared_memory.SharedMemory(name='SM1')
    mat=np.ndarray(sq.shape, dtype=sq.dtype, buffer=existing_shm.buf)
    while(h)
         sca.MFTEN_execute_cmd(debug,mat)#
    del mat
    existing_shm.close()

if __name__ == '__main__' :
    main()

    if h :
        sca= Sca(id_card, 2, gbt_ch, board, debug) ##

        root = Tk()
        root.geometry('500x500')
        gui = GuiApp(master=root)

        mat=sca.MFTEN_load(debug) 
        mat=np.array(mat)

        shm= shared_memory.SharedMemory(name='SM1', create=True, size=mat.nbytes)
        sq=np.ndarray(mat.shape, dtype=mat.dtype, buffer=shm.buf) 
        sq[:]=mat[:]

        t1=multiprocessing.Process(target=gui.createWidgets, args=(sq,))
        t1.start()
        t2=multiprocessing.Process(target=sequence_loop, args=(sq,))
        t2.start()
        t1.join()
        t2.join()

        del sq
        shm.close()
        shm.unlink()


