# -*- coding: utf-8 -*-
# @Author:varcer
#实现http/https代理
import socket
import multiprocessing
import re
import threading
import time
import conf
import pandas as pd
def proxy(cport='8080',ip='127.0.0.1',sport='8082'):
    print('开始监听:',ip,' ',cport)
    try:
        client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.bind((ip,int(cport)))
        client.listen(100)
        while 1:
            client_conn,addr=client.accept()
            p=multiprocessing.Process(target=client_server_http,args=(client_conn,))
            p.start()
            bigen=time.time()
            T=threading.Thread(target=clos,args=(bigen,p))
            T.start()
    except:
        pass

def client_server_https(client_socket,server_socket):
    while 1:
        try:
            client_data=client_socket.recv(1024*1024*5)
            if client_data:
                server_socket.sendall(client_data)
            else:
                client_socket.close()
                return 0
        except:
            client_socket.close()
            return 0

def server_client_https(client_socket,server_socket):
    while 1:
        try:
            server_data=server_socket.recv(1024*1024*5)
            if server_data:
                client_socket.sendall(server_data)
            else:
                client_socket.close()
                return 0
        except:
            client_socket.close()
            return 0

def client_server_http(client_conn):
    try:
        data=client_conn.recv(1024*1024*20)
        ip, port, temp,ssl= get_ip_port(data)
        print(ip, port)
        if ssl:
            simple_data = b'HTTP/1.1 200 Connection Established\r\n\r\n'
            client_conn.sendall(simple_data)
            server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_conn.connect((ip, int(port)))
            CT = threading.Thread(target=client_server_https, args=(client_conn, server_conn))
            ST = threading.Thread(target=server_client_https, args=(client_conn, server_conn))
            CT.start()
            ST.start()
        else:
            server_conn=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            server_conn.connect((ip,int(port)))
            client_data=adjust_data(data,temp)
            server_conn.sendall(client_data)
            while 1:
                temp=server_conn.recv(1024*1024*5)
                client_conn.sendall(temp)
                if not temp:
                    client_conn.close()
                    server_conn.close()
                    #sys.exit(0)
    except:
        pass

def get_ip_port_s(data):
    if 'CONNECT' in str(data):
        sreg = re.compile('CONNECT (.+:443) HTTP/1\.\d+')
        surl = sreg.findall(data.decode('utf-8'))[0]
        ip=surl.split(':')[0]
        port=surl.split(':')[1]
        ssl=True
        return ip,port,ssl
    return False,False,False

def get_ip_port(data):
    ssl=False
    if 'CONNECT' in str(data):
        sreg = re.compile('CONNECT (.+:443) HTTP/1\.\d+')
        surl = sreg.findall(data.decode('utf-8'))[0]
        ip = surl.split(':')[0]
        port = surl.split(':')[1]
        ssl = True
        temp=None
    else:
        reg=re.compile('.+ (.+) HTTP/1\.\d+')
        url=reg.findall(str(data))[0]
        temp=url.split('//')[1].split('/')[0]
        if ':' in temp:
            ip=temp.split(':')[0]
            port=temp.split(':')[1]
        else:
            ip=temp
            port='80'
    if conf.conf['second_proxy']:
        ip=pd.read_csv('iplist.csv')['ip   '].loc[conf.conf['index']]
        port =pd.read_csv('iplist.csv')['port'].loc[conf.conf['index']]
        conf.conf['index']=conf.conf['index']+1
        print(conf.conf['index'])
    return ip,port,temp,ssl
def adjust_data(data,temp):
    client_data=data.decode('utf-8').replace('http://'+temp,'',1)
    return bytes(client_data,'utf-8')

def clos(start,p):
    while 1:
        end=time.time()
        if (int(end)-int(start))==5:
            p.kill()
            break
if __name__=='__main__':
    port=input('输入监听端口:')
    proxy(cport=port)