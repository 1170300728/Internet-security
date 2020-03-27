# -*- coding: UTF-8 -*-

import socket
import sys
 
s = socket.socket() 
host = '192.168.0.104'
port = 1234  

try:
    s.connect((host, port))
except:
    print('connect失败！')
    sys.exit(1)

filename=input('输入文件名：')
s.send(filename.encode('utf-8'))
f=open(filename,'rb')
data=f.read(1024)
while True:
    s.send(data)
    data=f.read(1024)
    if not data:
        break
f.close()
print(1)
s.send('over'.encode('utf-8'))

print (s.recv(1024))
s.close()
