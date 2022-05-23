from MFH_Constant import *
from MFH_Core import *

import time
from futu import *
import tkinter as tk
import pandas as pd
import pytz
from datetime import datetime
from PyQt5.QtGui import QColor
from socketserver import BaseRequestHandler, ThreadingTCPServer
import threading
import queue


class OrderBookHandler(OrderBookHandlerBase):
    shm = None
    output_file = None
    feed_map = None

    def on_recv_rsp(self, rsp_str):
        # ret_code, data = super(OrderBookHandler, self).on_recv_rsp(rsp_str)
        # if ret_code != RET_OK:
        #     print("USOptionManual: error, msg: %s" % data)
        #     return RET_ERROR, data
        # if data['Bid'] == []: data["Bid"] = [()]
        # if data['Ask'] == []: data["Ask"] = [()]
        # # print("OrderBook ", data)
        # if self.b_dataRecord:
        #     pd.DataFrame(data).loc[0:0].to_csv(self.output_file, index=False,
        #                                        header=self.output_file.tell() == 0)
        # self.link_core.callback_orderbook(data)
        # return RET_OK, data
        ret_code, content = self.parse_rsp_pb(rsp_str)
        if ret_code == RET_OK:
            # print(content['code'])
            # print("{},{},{},{},{},{},{},{}".format(
            #                 content['svr_recv_time_bid'], content['code'],
            #                 content['Bid'][0][0], content['Bid'][0][1], content['Bid'][0][2],
            #                 content['Ask'][0][0], content['Ask'][0][1], content['Ask'][0][2]))
            # if content['code'] in OrderBookHandler.feed_map.prod_client_map:
            try:
                out_str = "0,OBUPDATE," + content['code'] + ",1,0"
                # out_str = str(content)
                for client in OrderBookHandler.feed_map.prod_client_map[content['code']]:
                    OrderBookHandler.feed_map.client_request_map[client].sendall(out_str.encode('utf-8'))
            except KeyError:
                print('============cant find key')
                # OrderBookHandler.feed_map.del_client[]
                # del OrderBookHandler.feed_map.prod_client_map[content['code']]

            # OrderBookHandler.shm[content['code']]['log'] = True
            if OrderBookHandler.shm is not None and OrderBookHandler.shm[content['code']] is not None:
                OrderBookHandler.shm[content['code']]['bid_p1'] = int(content['Bid'][0][0] * PRICE_ADJ)
                OrderBookHandler.shm[content['code']]['bid_q1'] = content['Bid'][0][1]
                OrderBookHandler.shm[content['code']]['bid_c1'] = content['Bid'][0][2]
                OrderBookHandler.shm[content['code']]['ask_p1'] = int(content['Ask'][0][0] * PRICE_ADJ)
                OrderBookHandler.shm[content['code']]['ask_q1'] = content['Ask'][0][1]
                OrderBookHandler.shm[content['code']]['ask_c1'] = content['Ask'][0][2]
                OrderBookHandler.shm[content['code']]['timestamp_bid'] = content['svr_recv_time_bid']
                OrderBookHandler.shm[content['code']]['timestamp_ask'] = content['svr_recv_time_ask']
                if OrderBookHandler.output_file and OrderBookHandler.shm[content['code']]['log']:
                    OrderBookHandler.output_file.write("{},{},{},{},{},{},{},{},{},{}".format(
                        content['svr_recv_time_bid'], content['svr_recv_time_ask'], content['code'],
                        content['Bid'][0][0], content['Bid'][0][1], content['Bid'][0][2],
                        content['Ask'][0][0], content['Ask'][0][1], content['Ask'][0][2], '\n'))
                    OrderBookHandler.output_file.flush()

        return ret_code, content


class TickerHandler(TickerHandlerBase):
    shm = None
    output_file = None
    feed_map = None

    def on_recv_rsp(self, rsp_str):
        # ret_code, data = super(TickerHandler, self).on_recv_rsp(rsp_str)
        # if ret_code != RET_OK:
        #     print("TickerTest: error, msg: %s" % data)
        #     return RET_ERROR, data
        # # print("Ticker ", data.to_dict('list'))
        # if self.b_dataRecord:
        #     pd.DataFrame(data).loc[0:0].to_csv(self.output_file, index=False,
        #                                        header=self.output_file.tell() == 0)
        # self.link_core.callback_ticker(data)
        #
        # return RET_OK, data
        ret_code, content = self.parse_rsp_pb(rsp_str)
        if ret_code != RET_OK:
            return ret_code, content
        else:
            # print(content)
            for trade_line in content:
                try:
                    out_str = "0,TDUPDATE," + trade_line['code'] + ",1,0"
                    # out_str = str(trade_line)
                    # print(trade_line)
                    for client in TickerHandler.feed_map.prod_client_map[trade_line['code']]:
                        TickerHandler.feed_map.client_request_map[client].sendall(out_str.encode('utf-8'))
                except KeyError:
                    print('============cant find key')
                if TickerHandler.shm is not None and TickerHandler.shm[trade_line['code']] is not None:
                    trade_idx = TickerHandler.shm[trade_line['code']]['trade_id'] + 1
                    trade_subidx = str(trade_idx % 5)
                    TickerHandler.shm[trade_line['code']]['trade_p' + trade_subidx] = int(float(trade_line['price']) * PRICE_ADJ)
                    TickerHandler.shm[trade_line['code']]['trade_q' + trade_subidx] = int(trade_line['volume'])
                    TickerHandler.shm[trade_line['code']]['trade_d' + trade_subidx] = (trade_line['ticker_direction'] == 'BUY')
                    TickerHandler.shm[trade_line['code']]['trade_id'] = trade_idx
                    if TickerHandler.output_file and TickerHandler.shm[trade_line['code']]['log']:
                        TickerHandler.output_file.write("{},{},{},{},{},{}".format(
                            trade_line['time'], trade_line['code'],
                            trade_line['price'], trade_line['volume'], trade_line['ticker_direction'], '\n'))
                        OrderBookHandler.output_file.write("{},{},{},{},{},{}".format(
                            trade_line['time'], trade_line['code'],
                            trade_line['price'], trade_line['volume'], trade_line['ticker_direction'], '\n'))
                        TickerHandler.output_file.flush()

            # return RET_OK, ticker_frame_table


class TradeOrderHandler(TradeOrderHandlerBase):
    """ order update push"""

    def __init__(self, main, file):  # member variables
        TradeOrderHandlerBase.__init__(self)
        # variables for front end display
        self.link_core = main
        self.b_dataRecord = False

        self.order_id = 0
        self.code = ""
        self.order_qty = 0.0
        self.order_price = 0.0
        self.order_trd_side = ""
        self.order_order_status = ""
        self.order_create_time = ""

        self.df_data = pd.DataFrame({})
        self.output_file = file

    def on_recv_rsp(self, rsp_pb):
        ret, data = super(TradeOrderHandler, self).on_recv_rsp(rsp_pb)
        if ret != RET_OK:
            print("OrderTest: error, msg: %s" % data)
            return RET_ERROR, data
        # print("Order ", data.to_dict('list'))
        if self.b_dataRecord:
            pd.DataFrame(data).loc[0:0].to_csv(self.output_file, index=False,
                                               header=self.output_file.tell() == 0)
        self.link_core.callback_order(data)
        return RET_OK, data


class TradeDealHandler(TradeDealHandlerBase):
    """ order update push"""

    def __init__(self, main, file):  # member variables
        TradeDealHandlerBase.__init__(self)
        # variables for front end display
        self.link_core = main
        self.b_dataRecord = False

        self.order_id = 0
        self.code = ""
        self.order_qty = 0.0
        self.order_price = 0.0
        self.order_trd_side = ""
        self.order_order_status = ""
        self.order_create_time = ""

        self.df_data = pd.DataFrame({})
        self.output_file = file

    def on_recv_rsp(self, rsp_pb):
        ret, data = super(TradeDealHandler, self).on_recv_rsp(rsp_pb)
        if ret != RET_OK:
            print("DealTest: error, msg: %s" % data)
            return RET_ERROR, data
        # print("Deal ", data.to_dict('list'))
        if self.b_dataRecord:
            pd.DataFrame(data).loc[0:0].to_csv(self.output_file, index=False,
                                               header=self.output_file.tell() == 0)
        self.link_core.callback_deal(data)
        return RET_OK, data


# class SocketSenderNewThread(threading.Thread):
#     def __init__(self, in_cnn, in_client_addr, in_feed_map):
#         threading.Thread.__init__(self)
#         self.cnn = in_cnn
#         self.client_address = in_client_addr
#         self.feed_map = in_feed_map
#
#
#     def run(self):
#         client_str = "{}({})".format(self.client_address[0], self.client_address[1])
#         while True:
#             try:
#                 self.cnn.sendall()
#                 SocketHandler.sys_log.log_out(['CMM', 'EVT'], client_str + " Send: " + out_str)
#             except ConnectionResetError:
#                 break


class SocketHandler(BaseRequestHandler):
    sys_log = None
    call_back_func = None
    feed_map = None

    def handle(self):
        address, pid = self.client_address
        if SocketHandler.feed_map:
            self.feed_map.client_request_map[self.client_address] = self.request
        client_str = "{}({})".format(address, pid)
        if SocketHandler.sys_log:
            SocketHandler.sys_log.log_out(['SYS', 'CMM'], client_str + " Connected")
        while True:
            try:
                data = self.request.recv(BUFF_SIZE)
                if len(data) > 0 and data != b'q':
                    in_str = data.decode('utf-8')
                    if SocketHandler.sys_log:
                        SocketHandler.sys_log.log_out(['CMM', 'EVT'], client_str + " Recv: " + in_str)
                    out_str = ''
                    if SocketHandler.call_back_func:
                        out_str = SocketHandler.call_back_func(in_str, self.client_address)
                    print(out_str)
                    if len(out_str) > 0 and SocketHandler.feed_map:
                        self.request.sendall(out_str.encode('utf-8'))
                    cur_threading = threading.current_thread()
                else:
                    self.request.close()
                    self.feed_map.del_client(self.client_address)
                    if SocketHandler.sys_log:
                        SocketHandler.sys_log.log_out(['SYS', 'CMM'], client_str + " Disconnected")
                    break
            except ConnectionResetError:
                self.request.close()
                self.feed_map.del_client(self.client_address)
                if SocketHandler.sys_log:
                    SocketHandler.sys_log.log_out(['SYS', 'CMM'],
                                                  client_str + " Disconnected With ConnectionResetError")
                break
            except OSError:
                self.request.close()
                self.feed_map.del_client(self.client_address)
                if SocketHandler.sys_log:
                    SocketHandler.sys_log.log_out(['SYS', 'CMM'],
                                                  client_str + " Disconnected With OSError")
                break
