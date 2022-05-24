from MarketFeedHandler.MFH_Constant import *

import socket
import sys
import threading
import time


class ClientReceiverNewThread(threading.Thread):
    def __init__(self, in_core, in_cnn):
        threading.Thread.__init__(self)
        self.cnn = in_cnn
        self.core_link = in_core

    def run(self):
        while True:
            try:
                recv_data = self.cnn.recv(BUFF_SIZE)
                if len(recv_data) > 0:
                    in_str = recv_data.decode('utf-8')
                    print('receive:', in_str)
                    self.core_link.data_communication(in_str)
            except OSError:
                break
        print('receiver closed')


class ClientSenderNewThread(threading.Thread):
    def __init__(self, in_core):
        threading.Thread.__init__(self)
        self.core_link = in_core
        self.sock = socket.socket()

    def run(self):
        self.sock.connect((MFH_IP, MFH_SOCKET_PORT))
        print('have connected with server')

        r = ClientReceiverNewThread(self.core_link, self.sock)
        r.start()
        # try:
            # while True:
            # for i in range(5):
            # data = "1,HEARTBEAT,NONE,1,0"
            # self.sock.sendall(data.encode('utf-8'))
            # print('send:', data)
            # data = "1,SUBSCRIBE,US.TSLA220520C735000,1"
            # self.sock.sendall(data.encode('utf-8'))
            # print('send:', data)
            # # data = "2,UNSUBSCRIBE,US.TSLA220513C855000,1"
            # # self.sock.sendall(data.encode('utf-8'))
            # # print('send:', data)
            # # time.sleep(0.5)
            # time.sleep(700)
            # data = "2,UNSUBSCRIBE,US.TSLA220520C735000,1"
            # self.sock.sendall(data.encode('utf-8'))
            # print('send:', data)
            # time.sleep(5)
            # self.sock.sendall('q'.encode('utf-8'))
            # print('Sender closed!')
            # self.sock.close()
            # r.join()
        # except ConnectionResetError:
        #     print('MFH is down!')
        #     print('Sender closed!')
        #     self.sock.close()
        #     r.join()
            # sys.exit()

    def __del__(self):
        self.sock.close()
