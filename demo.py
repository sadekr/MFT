#!/usr/bin/env python3.8
import ctypes
import sys
import multiprocessing
import time
from tkinter import *
import fileinput
from random import random
from random import seed
from multiprocessing import shared_memory
import numpy as np 

class GuiApp(Frame):                                                                                  
    def __init__(self, master=None):
        Frame.__init__(self, master)                                                                
        self.pack()
        #self.createWidgets()
        #self.mainloop()

    def print_contents(self, event):
        print("Entry content is: ", \
              self.contents.get())

    def read_value(self, e):
        print(d.shape)
        label = Label(root, text= e[1][0], width=20, font=("bold",10))
        label.place(x=70,y=130)

    def read_value1(self, e):
        label = Label(root, text= e[1][2], width=20, font=("bold",10))
        label.place(x=70,y=200)
    
    def change_value(self, e,b): 
        e[1][0] = 55555
        print(e[1][0],b[1][0])
        print(e,b)

    def createWidgets(self, b):                                      
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
        e=np.ndarray(b.shape, dtype=b.dtype, buffer=existing_shm.buf)
        #e=b # obligatoire? 
        button1=Button(self, text=" Value of mat[1][0] ", command = lambda : self.read_value(e))
        button1.pack()
        button3=Button(self, text=" Value of mat[1][2] ", command = lambda : self.read_value1(e))
        button3.pack()
        button2=Button(self, text=" Change mat[1][0] ", command = lambda : self.change_value(e,b))
        button2.pack()
        self.mainloop()
        print("///////////////////")
        print(e,b)
        del e
        existing_shm.close()

def matrix_to_share(): 
    file_name = 'trycmds.txt'
    line_num = 0
    d=[]
    with open(file_name, 'r') as f:
        data_file = [l for l in (line.strip() for line in f) if l] 
    for line in data_file:
        line_num = line_num + 1
        if line[0] == '#':
            print(line)
            continue
        l =  line.split(" ")
        if (len(l)==2) : l.append('0')
        d.append([int(x,0) for x in l])
    return d

def boucle_test(b):

    existing_shm=shared_memory.SharedMemory(name='SM1')
    e=np.ndarray(b.shape, dtype=b.dtype, buffer=existing_shm.buf)
    #e=b

    while (1):
        e[2][2]=int(random()*100)
        print(e,e[2][2])     #get?? 
        time.sleep(3)
        #rawInput 

if __name__ == '__main__' :
    root = Tk()
    root.geometry('500x500')
    gui = GuiApp(master=root)

    d=matrix_to_share()    
    d=np.array(d)
    print(d.shape)
    shm= shared_memory.SharedMemory(name='SM1', create=True, size=d.nbytes)
    b=np.ndarray(d.shape, dtype=d.dtype, buffer=shm.buf) 
    b[:]=d[:]
    print(b)
    print('#########################')
    t1=multiprocessing.Process(target=gui.createWidgets, args=(b,))
    t1.start()
    t=multiprocessing.Process(target=boucle_test, args=(b,))
    t.start()

    seed(1) 

    print("----------------------")  # le changement de b/e est pas pris hors la classe GUIAPP 
    print(b)
    time.sleep(5)
    print("----------------------")
    print(b)

    t1.join()
    t.join()

    del b
    shm.close()
    shm.unlink()


