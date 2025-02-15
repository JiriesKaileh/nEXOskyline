from tkinter import *
import socket
from threading import Thread
import time
import datetime
import sys
import os
import random
import struct
import matplotlib.pyplot as plt
# from matplotlib.figure import Figure

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)


class grafit(Frame):
    def on_closing(self):
        self.run = False
        os._exit(0)

    def set_dc(self, dat=0.5):  # set the duty cycle (PULSED mode only)
        if self.btn_var.get() == 'CW':  # if CW, turn ON/OFF the solenoid
            msg = self.btn_var.get() + self.btn_var2.get() + '\n'
            self.ser.send(msg.encode('iso-8859-1'))
            return
        if self.btn_var2.get() == 'ON':  # turn on the pulsing
            msg = str(dat)
        else:
            msg = self.btn_var2.get()  # turn off the pulsing
        msg = msg + '\n'
        self.ser.send(msg.encode('iso-8859-1'))

    def plotit(self):
        while True :
            self.is_running = (self.btn_var3.get() == 'STOP')
            if self.is_running == False :
                continue
            self.ser.send('???\n'.encode())
            c=''
            data = ''
            while c != '\n' :
    	        c = self.ser.recv(1).decode()
    	        data = data + c
            print('received '+data)
            volt = float(data)
            volt = ((volt/1024.0)*5.0)/6.0 #conversion from counts to current assuming 10 bits, 6 ohms

            self.xar.append((time.time() - self.start_time) / 3600.0)
            self.yar.append(volt)
            if len(self.xar) > 86400:
                self.xar.pop(0)
                self.yar.pop(0)
            print("getting here")
            #plt.cla()
            plt.plot(self.xar, self.yar, 'ro-')
            plt.title("Current vs Time")
            plt.ylabel('Current (A)')
            plt.xlabel('Time (hours)')
            #self.plot_widget.grid(row=0, column=2)
            self.fig.canvas.draw()

            time.sleep(1.0)


    def __init__(self):
        self.window = Tk()
        self.window.geometry('750x625')
        self.window.title('XPM Shutter Control')
        self.ser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ser.connect(('10.0.0.4', 5047))  # Arduino server connection

        Label(self.window, text='DC [%]').grid(column=3, row=2) # slider label

        self.xar = []
        self.yar = []
        self.is_running = False

        # duty cycle slider
        self.dc_var = DoubleVar(self.window, 50.0)
        self.dc_slider = Scale(self.window, command=self.set_dc, orient=HORIZONTAL, resolution=-1, from_=10.0, to=100.0,
                               variable=self.dc_var)
        self.dc_slider.grid(column=3, row=3)

        # DC/pulse button
        self.btn_var = StringVar(self.window, 'CW')
        LABEL0, LABEL1 = 'CW', 'PULSED'
        self.xr = Checkbutton(self.window, textvariable=self.btn_var, width=12, variable=self.btn_var,
                              offvalue=LABEL0, onvalue=LABEL1, indicator=False, command=self.set_dc)
        self.xr.grid(column=3, row=1)

        # solenoid ON/OFF
        self.btn_var2 = StringVar(self.window, 'OFF')
        LABEL2, LABEL3 = 'ON', 'OFF'
        self.sol = Checkbutton(self.window, textvariable=self.btn_var2, width=12, variable=self.btn_var2,
                               offvalue=LABEL3, onvalue=LABEL2, indicator=False, command=self.set_dc)
        self.sol.grid(column=3, row=4)

        # start/stop graphing
        self.btn_var3 = StringVar(self.window, 'START')
        LABEL4, LABEL5 = 'START', 'STOP'
        self.st = Checkbutton(self.window, textvariable=self.btn_var3, width=12, variable=self.btn_var3,
                               offvalue=LABEL4, onvalue=LABEL5, indicator=False)
        self.st.grid(column=3, row=5)
        self.plotter = Thread(target=self.plotit)
        self.plotter.start()
        self.start_time = time.time()

        Label(self.window, text=' ').grid(row=2)
        self.window.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.fig = plt.figure(1)
        plt.subplot(111)
        self.fig.text(0.5,0.04,'Time (Hours)',ha ='center',va = 'center')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.plot_widget = self.canvas.get_tk_widget()
        self.plot_widget.grid(row=0, column=2)

        self.fig.canvas.draw()
        self.window.mainloop()


        self.cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        HOST = '10.0.0.4'
        PORT = 5047

        self.cli_sock.connect((HOST,PORT))
        self.window = Tk()
        self.window.title('Remote data')
        self.fig = plt.figure(1)
        plt.subplot(111)
        self.fig.text(0.5,0.04,'Time (Hours)',ha ='center',va = 'center')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.plot_widget = self.canvas.get_tk_widget()
        self.plot_widget.grid(row=0, column=2)

        self.fig.canvas.draw()


        self.plotter.start()  # start plotting data
        self.window.mainloop()

appl = grafit()
