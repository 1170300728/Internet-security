#!/usr/bin/python
# -*- coding: UTF-8 -*-
from tkinter import *
import tkinter.messagebox
import socket
import threading

#线程代码，调用try_connect函数进行扫描尝试
class myThread (threading.Thread):
    def __init__(self, threadID, hostnum, portnum, portlist):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.hostnum = hostnum
        self.portnum = portnum
        self.portlist = portlist
    def run(self):
        try_connect(self.hostnum, self.portnum, self.portlist)

#主要UI部分
class scanner():
    def __init__(self,window):
        self.window=window

        self.scanner_frame = Frame(self.window)

        #各种输入框UI
        Label(self.scanner_frame, text="请输入线程数：").pack(side=TOP, padx=5, pady=10)
        self.thread_num_entry = Entry(self.scanner_frame, width=50)
        self.thread_num_entry.pack(side=TOP)

        Label(self.scanner_frame, text="请输入ip最小值（默认为192.168.0.xxx，即输入最多三位，0-255）：").pack(side=TOP, padx=5, pady=10)
        self.ip_min_entry = Entry(self.scanner_frame, width=50)
        self.ip_min_entry.pack(side=TOP)

        Label(self.scanner_frame, text="请输入ip最大值：").pack(side=TOP, padx=5, pady=10)
        self.ip_max_entry = Entry(self.scanner_frame, width=50)
        self.ip_max_entry.pack(side=TOP)

        Label(self.scanner_frame, text="请输入端口最小值：").pack(side=TOP, padx=5, pady=10)
        self.port_min_entry = Entry(self.scanner_frame, width=50)
        self.port_min_entry.pack(side=TOP)

        Label(self.scanner_frame, text="请输入端口最大值：").pack(side=TOP, padx=5, pady=10)
        self.port_max_entry = Entry(self.scanner_frame, width=50)
        self.port_max_entry.pack(side=TOP)

        #输出框设置，初始设为空，等待后续修改其内容即可输出port列表
        self.displaytxt=StringVar()
        self.txt = Label(self.scanner_frame,textvariable=self.displaytxt)
        self.txt.pack(side=BOTTOM)

        self.scanner_frame.pack()

        #“开始”按钮UI，按下后调用start_scan函数开始扫描
        self.b=Button(self.scanner_frame, text="开始", command=self.start_scan)
        self.b.pack(side=BOTTOM)

    #开始扫描函数，依据按下“开始”按钮时，输入框中的数据，判断数据合理性，如果数据合理，开始扫描；如果不合理，打印警告并等待修改数据
    def start_scan(self,):
        #数据获取
        threadNum = self.thread_num_entry.get()
        minIP = self.ip_min_entry.get()
        maxIP = self.ip_max_entry.get()
        minPort = self.port_min_entry.get()
        maxPort = self.port_max_entry.get()

        #对空值赋默认值，并判断数据合理性
        if minIP == '':
            minIP = 0
        if maxIP == '':
            maxIP = 255
        if minPort == '':
            minPort = 0
        if maxPort == '':
            maxPort =65535
        if threadNum == '':
            threadNum = 5 
        threadNum = int(threadNum)
        minIP = int(minIP)
        maxIP = int(maxIP)
        minPort = int(minPort)
        maxPort = int(maxPort)
        if maxIP<minIP or maxPort<minPort or maxIP>255 or minIP<0 or maxPort>65535 or minPort<0:
            self.displaytxt.set("含有错误参数，请重新输入")
            return
        
        #数据合理，开始利用线程扫描
        threadid=1
        threads=[]
        portlist=[]
        #按照IP和端口号范围循环
        for hostnum in range(minIP,maxIP+1):
            for portnum in range(minPort,maxPort+1):
                #如果线程数达到上限等待线程动作结束后再启动下一轮线程
                if threadid>threadNum:
                    for t in threads:
                        t.join()
                    threads.clear()
                    threadid=1
                    thread = myThread(threadid,hostnum,portnum,portlist)
                    thread.start()
                    threads.append(thread)
                    threadid=threadid+1
                else:
                    thread = myThread(threadid,hostnum,portnum,portlist)
                    thread.start()
                    threads.append(thread)
                    threadid=threadid+1
        #所有IP和端口号都已被处理线程解决或正在解决，等待线程池中线程全部结束
        for t in threads:
            t.join()
        self.displaytxt.set(','.join(portlist))
        #输入到文件中
        f = open('ports.txt','w')
        f.write(','.join(portlist))
        f.close()

#尝试连接函数，主要利用connect失败会有异常状态，用异常处理判断目标IP及端口号是否开启
def try_connect(hostnum, portnum, portlist):
    s = socket.socket() 
    host = '192.168.0.'+str(hostnum) 
    port = portnum     
    
    try:
        s.connect((host, port))
    except:
        return
    else:
        s.close()
        #可以连接，认为目标端口开启，将该端口加入端口列表
        portlist.append(str(portnum))

if __name__ == '__main__':
    window= Tk()
    window.title("端口扫描系统")

    #启动系统
    scanner(window)

    window.mainloop()
