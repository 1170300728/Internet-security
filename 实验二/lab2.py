import pcap
import dpkt
from pylibpcap import get_first_iface

sniffer = pcap.pcap(name=get_first_iface())  
sniffer.setfilter("tcp")                 
i=0  
out = ''
capIP =  (0, 0, 0, 0, 0)
capport = -1
capcount = 0
for packet_time, packet_data in sniffer:
    print("***********")
    packet = dpkt.ethernet.Ethernet(packet_data)

    srcIP = tuple(list(packet.data.src))
    dstIP = tuple(list(packet.data.dst))
    srcport = packet.data.data.sport
    dstport = packet.data.data.dport

    print("源IP:%d.%d.%d.%d" % srcIP)
    print("目的IP:%d.%d.%d.%d" % dstIP)
    print("源端口:%d" % srcport)
    print("目的端口:%d" % dstport)

    t = packet.data.data.data[:]
    print("有效载荷:")
    print(t)
    print()

    if dstIP == (192, 168, 0, 104) and dstport == 1234:
        if capport == -1:
            capport = srcport
            capIP = srcIP
            capcount += 1
        elif capport == srcport and capIP == srcIP:
            data = t.decode('utf-8')
            if capcount < 2:
                capcount +=1 
            elif capcount == 2:
                f = open(data,'w')
                capcount += 1
            elif data == 'over':
                f.close()
                break
            else:
                f.write(data)

