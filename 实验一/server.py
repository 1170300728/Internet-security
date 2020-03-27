import socket              
import sys
import re

s = socket.socket()
host = '192.168.0.104'
port = 1234

try:
    s.bind((host, port))
except:
    print('bind失败！')
    sys.exit(1)

s.listen(5)
while True:
    c,addr = s.accept()
    print ('连接地址：', addr)
    fdata=c.recv(1024)
    print (fdata)
    if re.match(r'.*.txt',fdata.decode('utf-8')):
        f = open(fdata.decode('utf-8'),'wb')
        while True:
            data=c.recv(1024)
            print(data)
            if data.decode('utf-8')=='over':
                break
            f.write(data)
        f.close()
    c.send('bye!'.encode('utf-8'))
    c.close()
