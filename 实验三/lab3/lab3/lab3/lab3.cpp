#define _CRT_SECURE_NO_WARNINGS
#define _WINSOCK_DEPRECATED_NO_WARNINGS

#include <stdio.h>  
#include <stdlib.h>  
#include <string.h>  
#include <WinSock2.h>  
#include <windows.h> 

#define PORT 5000  
#define SERVER_IP "192.168.61.128"  
#define BUFFER_SIZE 1024  
#define FILE_NAME_MAX_SIZE 512  
#pragma comment(lib, "WS2_32")  

int main()
{
	// ��ʼ��socket dll  
	WSADATA wsaData;
	WORD socketVersion = MAKEWORD(2, 0);
	if (WSAStartup(socketVersion, &wsaData) != 0)
	{
		printf("Init socket dll error!");
		exit(1);
	}

	int lfd, ret = 0;
	lfd = socket(AF_INET, SOCK_DGRAM, 0);

	//��װ�׽��ֵ�ַ�ṹ
	struct sockaddr_in saddr, caddr;
	caddr.sin_family = AF_INET;
	caddr.sin_port = htons(5555);
	caddr.sin_addr.s_addr = inet_addr("127.0.0.1");

	//���׽��ֵ�ַ���׽���������
	//ret = bind(lfd, (struct sockaddr*) & caddr, sizeof(caddr));
	if (ret < 0)
	{
		perror("bind fail:");
		return -1;
	}
	//��װ�׽��ֵ�ַ�ṹ

	saddr.sin_family = AF_INET;
	saddr.sin_port = htons(PORT);
	saddr.sin_addr.s_addr = inet_addr(SERVER_IP);

	char buf[1024] = "test udp protcol !";
	int addrlen;

	while (1)
	{
		/*һֱ��saddr�ĵ�ַ�����ն�IP�Ͷ˿ںţ�������udp��*/
		memset(buf, 0, 1024);
		scanf("%s", buf);
		sendto(lfd, buf, 1024, 0, (struct sockaddr*) & saddr, sizeof(saddr));
		system("pause");
	}
	closesocket(lfd);

	return 0;


}