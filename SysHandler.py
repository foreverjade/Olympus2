import time
from futu import *
import tkinter as tk
import pandas as pd
import pytz
from datetime import datetime
from PyQt5.QtGui import QColor
from socketserver import BaseRequestHandler, ThreadingTCPServer
import threading

BUFF_SIZE = 1024


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
            if content['code'] in OrderBookHandler.feed_map.prod_client_map:
                for client in OrderBookHandler.feed_map.prod_client_map[content['code']]:
                    OrderBookHandler.feed_map.client_queue_map[client].put(content)

            if OrderBookHandler.shm and content['code'] in OrderBookHandler.shm:
                OrderBookHandler.shm[content['code']]['bid_p1'] = content['Bid'][0][0]
                OrderBookHandler.shm[content['code']]['bid_q1'] = content['Bid'][0][1]
                OrderBookHandler.shm[content['code']]['bid_c1'] = content['Bid'][0][2]
                OrderBookHandler.shm[content['code']]['ask_p1'] = content['Ask'][0][0]
                OrderBookHandler.shm[content['code']]['ask_q1'] = content['Ask'][0][1]
                OrderBookHandler.shm[content['code']]['ask_c1'] = content['Ask'][0][2]
                OrderBookHandler.shm[content['code']]['timestamp'] = 0
                if OrderBookHandler.output_file and OrderBookHandler.shm[content['code']]['log']:
                    OrderBookHandler.output_file.write("{},{},{},{},{},{},{},{},{}".format(
                        content['svr_recv_time_bid'], content['code'],
                        content['Bid'][0][0], content['Bid'][0][1], content['Bid'][0][2],
                        content['Ask'][0][0], content['Ask'][0][1], content['Ask'][0][2], '\n'))
                    OrderBookHandler.output_file.flush()

        # return ret_code, content


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
                # self.shm[trade_line['code']]['bid_p1'] = trade_line['Bid'][0][0]
                if OrderBookHandler.output_file:
                    OrderBookHandler.output_file.write("{},{},{},{},{},{}".format(
                        trade_line['time'], trade_line['code'],
                        trade_line['price'], trade_line['volume'], trade_line['ticker_direction'], '\n'))
                    OrderBookHandler.output_file.flush()

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


class SocketHandler(BaseRequestHandler):
    sys_log = None
    call_back_func = None
    # feed_map = None

    def handle(self):
        address, pid = self.client_address
        client_str = "{}({})".format(address, pid)
        if SocketHandler.sys_log:
            SocketHandler.sys_log.log_out(['SYS', 'CMM'], client_str + " Connected")
        while True:
            # if SocketHandler.feed_map and (address, pid) in SocketHandler.feed_map.client_queue_map:
            #     q = SocketHandler.feed_map.client_queue_map[(address, pid)]
            #     while not q.empty():
            #         out_str = str(q.get())
            #         print ('==================',out_str)
            #         self.request.sendall(out_str.encode('utf-8'))

            data = self.request.recv(BUFF_SIZE)
            if len(data) > 0:
                in_str = data.decode('utf-8')
                if SocketHandler.sys_log:
                    SocketHandler.sys_log.log_out(['CMM', 'EVT'], client_str + " Recv: " + in_str)
                if SocketHandler.call_back_func:
                    out_str = SocketHandler.call_back_func(in_str, (address, pid))
                else:
                    out_str = 'response'
                self.request.sendall(out_str.encode('utf-8'))
                if SocketHandler.sys_log:
                    SocketHandler.sys_log.log_out(['CMM', 'EVT'], client_str + " Send: " + out_str)
                cur_threading = threading.current_thread()
            else:
                if SocketHandler.sys_log:
                    SocketHandler.sys_log.log_out(['SYS', 'CMM'], client_str + " Disconnected")
                break

        pass
