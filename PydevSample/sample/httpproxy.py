# socket サーバを作成

import socket
import re
import threading

#接続先、portを取得
def getConnectInfo(data):
    result = re.match("^CONNECT\\s+([^\\s]+)\\s+([^\\s]+)", data.decode('utf-8'))
    pair = result.group(1).split(":")
    return (pair[0], int(pair[1]))

def tunnelRequest(cs, ss):
    while True:
        data_request = cs.recv(1024*1024)
        print('data_request:{}'.format(data_request))
        print(len(data_request))
        if not data_request:
            print('recv failed(cli)')
            return

        ss.sendall(data_request);

def tunnelResponse(cs, ss):
    while True:  
        #サーバから応答受信
        data_response = ss.recv(1024*1024); 
        print('data_response:{}'.format(data_response))
        print(len(data_response))

        if not data_response:
            print('recv failed(dst)')
            return
        
        #クライアントへデータ送信
        cs.sendall(data_response)

def doSession(conn):
    with conn:
        # データを受け取る
        data = conn.recv(1024*1024)
        if not data:
            print('first recv failed')
            return
        print('data : {}'.format(data))

        # 目的のサーバに接続
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as d:
            address = getConnectInfo(data)
            print(address[0])
            print(address[1])
            #perhapsNoneType = d.connect(address) 
            #print(type(perhapsNoneType))
            d.connect(address) 
            
            #クライアントに接続完了応答送信
            conn.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')

            #要求トンネル用スレッド
            t1 = threading.Thread(target=tunnelRequest, args=(conn, d))
            t1.setDaemon(True)

            t2 = threading.Thread(target=tunnelResponse, args=(conn, d))
            t2.setDaemon(True)

            t1.start()
            t2.start()

            t1.join()
            t2.join()

# AF = IPv4 という意味
# TCP/IP の場合は、SOCK_STREAM を使う
def execService():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # IPアドレスとポートを指定
        s.bind(('127.0.0.1', 50007))
        # 1 接続
        s.listen(10)
        # 誰かがアクセスしてきたら、コネクションとアドレスを入れる
        while True:
            conn, addr = s.accept()
            t0 = threading.Thread(target=doSession, args=(conn,))
            t0.setDaemon(True)
            t0.start()

#サービス実行
execService()