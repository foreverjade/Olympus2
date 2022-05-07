#  the core part of Olympus Trading System

from socketserver import ThreadingTCPServer

from SysSharedMemory import *
from SysHandler import *
from SysManager import *
from SysLog import *


# from old.SysWindow import *
# import cgitb
#
# cgitb.enable(format='text')
#
# import threading


class SysCore:
    version = "Olympus Beta 1.0.0507"
    heart = "For my forever love, Ying"

    # login info
    ip = '127.0.0.1'
    port = 11111
    pwd_unlock = '900213'

    # internal communication
    soc_port = 22222
    event_id = 1

    def __init__(self):

        # sub systems
        self.shm = SysShardMemory(self, 100)
        self.sys_file = SysFileManager(self)
        self.sys_log = SysLog(self)
        self.sys_feed = SysFeedManager()
        # self.sys_stg_mgr = SysStrategyManager(self)
        # self.sys_pos_mgr = SysPositionManager(self)
        # self.sys_ord_mgr = SysOrderManager(self)
        # self.sys_log.log_out("Subsystems Launched Successfully!")

        # futu component
        self.sys_log.log_out(['SYS'], '=========================NEW PROGRAMME=======================')
        self.quote_ctx = OpenQuoteContext(host=SysCore.ip, port=SysCore.port)
        self.sys_log.log_out(['SYS'], 'Connection established!')
        OrderBookHandler.shm = self.shm
        OrderBookHandler.output_file = self.sys_file.file_quote_handler_output
        OrderBookHandler.feed_map = self.sys_feed
        self.quote_handler = OrderBookHandler()
        if self.quote_ctx.set_handler(self.quote_handler) == RET_OK:
            self.sys_log.log_out(['SYS'], 'Quote Handler is ready!')
        TickerHandler.shm = self.shm
        TickerHandler.output_file = self.sys_file.file_ticker_handler_output
        TickerHandler.feed_map = self.sys_feed
        self.ticker_handler = TickerHandler()
        if self.quote_ctx.set_handler(self.ticker_handler) == RET_OK:
            self.sys_log.log_out(['SYS'], 'Ticker Handler is ready!')

        self.set_socket_handler(SysCore.ip, SysCore.soc_port)
        self.sys_log.log_out(['SYS'], 'Internal Socket Handler is ready!')

        # self.feed_subscribe('US.TSLA220513C855000')
        # self.feed_unsubscribe('US.TSLA220513C855000')

        # self.trd_ctx_us = OpenUSTradeContext(host=Core.ip, port=Core.port)
        # self.trd_ctx_hk = OpenHKTradeContext(host=Core.ip, port=Core.port)
        # self.trd_ctx_cn = OpenCNTradeContext(host=Core.ip, port=Core.port)
        # self.trd_ctx_current = self.trd_ctx_us
        # self.order_handler = TradeOrderHandler(self, self.sys_file.file_order_handler_output)
        # self.deal_handler = TradeDealHandler(self, self.sys_file.file_deal_handler_output)
        # self.trd_ctx_us.set_handler(self.order_handler)
        # self.trd_ctx_us.set_handler(self.deal_handler)
        # self.trd_ctx_hk.set_handler(self.order_handler)
        # self.trd_ctx_hk.set_handler(self.deal_handler)
        # self.trd_ctx_cn.set_handler(self.order_handler)
        # self.trd_ctx_cn.set_handler(self.deal_handler)
        # self.sys_log.log_out("Connection Built Successfully!")
        #
        # self.data_account_status = pd.DataFrame({})
        # self.data_account_details = pd.DataFrame({})
        # self.option_chain_filter = OptionDataFilter()
        # self.data_option_chain = pd.DataFrame({})
        # self.data_position_list = pd.DataFrame({})
        # self.data_order_list = pd.DataFrame({})
        # self.data_deal_list = pd.DataFrame({})
        # self.data_historical_order_list = pd.DataFrame({})
        #
        # # Pyqt5
        # self.app = QApplication(sys.argv)
        # self.msg_box = QMessageBox()
        # self.olympusWin = OlympusMainWindow(self)
        # self.olympusWin.show()
        # self.sys_log.log_out("Window Launched Successfully!")
        # sys.exit(self.app.exec_())

    def event_process(self, in_str, client_pair):
        '''
        [EVENTID, EVENT, CODE, VALUE, ADDITIONAL ...]
        SAMPLE: "1,SUBSCRIBE,US.TSLA220513C855000,1"
        [EVENTID, EVENT, CODE, EVENTID_IN, STATUS, REMARK ...]
        SAMPLE: "1,RESPONSE,US.TSLA220513C855000,1,1,SUBSCRIBE Subscribe Successfully"
        '''

        IN_EVENTID = 0
        IN_EVENT = 1
        IN_CODE = 2
        IN_VALUE = 3
        IN_ADDITIONAL = 4

        OUT_EVENTID = 0
        OUT_EVENT = 1
        OUT_CODE = 2
        OUT_EVENTID_IN = 3
        OUT_STATUS = 4
        OUT_REMARK = 5

        in_list = in_str.split(',')
        if in_list[IN_EVENT] == 'SUBSCRIBE':
            self.sys_feed.add_pair((client_pair, in_list[IN_CODE]))
            status, message = self.feed_subscribe(in_list[IN_CODE])
            if status:
                message = in_list[IN_CODE] + " Subscribe Successfully"
            else:
                self.sys_feed.del_pair((client_pair, in_list[IN_CODE]))
            return "{},{},{},{},{},{}".format(SysCore.event_id, "RESPONSE", in_list[IN_CODE],
                                              in_list[IN_EVENTID], status + 0, message)
        elif in_list[IN_EVENT] == 'UNSUBSCRIBE':
            self.sys_feed.del_pair((client_pair, in_list[IN_CODE]))
            if in_list[IN_CODE] not in self.sys_feed.prod_client_map:
                status, message = self.feed_unsubscribe(in_list[IN_CODE])
                if status:
                    message = in_list[IN_CODE] + " Unsubscribe Successfully"
                else:
                    self.sys_feed.add_pair((client_pair, in_list[IN_CODE]))
                return "{},{},{},{},{},{}".format(SysCore.event_id, "RESPONSE", in_list[IN_CODE],
                                                  in_list[IN_EVENTID], status + 0, message)

    def set_socket_handler(self, host, port):
        SocketHandler.sys_log = self.sys_log
        SocketHandler.call_back_func = self.event_process
        SocketHandler.feed_map = self.sys_feed
        server = ThreadingTCPServer((host, port), SocketHandler)
        self.sys_log.log_out(['SYS'], 'Listening Internal Socket!')
        server.serve_forever()
        return True

    #
    # def get_acc_list(self, text):
    #     if text == 'US':
    #         self.trd_ctx_current = self.trd_ctx_us
    #     elif text == 'HK':
    #         self.trd_ctx_current = self.trd_ctx_hk
    #     else:
    #         self.trd_ctx_current = self.trd_ctx_cn
    #     ret, data = self.trd_ctx_current.get_acc_list()
    #     if ret == RET_OK:
    #         self.data_account_status = data
    #         self.accinfo_query(data['acc_id'][0])
    #     else:
    #         self.sys_log.log_out('[Error]' + data)
    #         self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)
    #
    # def accinfo_query(self, text2):
    #     self.trd_ctx_current.unlock_trade(self.pwd_unlock)
    #     ret2, data2 = self.trd_ctx_current.accinfo_query(
    #         trd_env=TrdEnv.REAL if int(text2) > 99999999 else TrdEnv.SIMULATE,
    #         acc_id=int(text2))
    #     if ret2 == RET_OK:
    #         self.data_account_details = data2
    #
    #         self.position_list_query(acc_type=TrdEnv.REAL if int(text2) > 99999999 else TrdEnv.SIMULATE,
    #                                  acc_id=int(text2))
    #         self.order_list_query(acc_type=TrdEnv.REAL if int(text2) > 99999999 else TrdEnv.SIMULATE,
    #                               acc_id=int(text2))
    #         self.historical_order_list_query(acc_type=TrdEnv.REAL if int(text2) > 99999999 else TrdEnv.SIMULATE,
    #                                          acc_id=int(text2))
    #         self.deal_list_query(acc_type=TrdEnv.REAL if int(text2) > 99999999 else TrdEnv.SIMULATE,
    #                              acc_id=int(text2))
    #     else:
    #         self.sys_log.log_out('[Error]' + data2)
    #         self.msg_box.warning(self.msg_box, 'Error', data2, QMessageBox.Close, QMessageBox.Close)
    #
    # def get_option_chain(self, security_code, expire_date):
    #     ret, data = self.quote_ctx.get_option_chain(security_code, IndexOptionType.NORMAL, '2020-12-01',
    #                                                 expire_date, OptionType.ALL, OptionCondType.ALL,
    #                                                 self.option_chain_filter)
    #     if ret == RET_OK:
    #         if len(data) > 0:
    #             self.data_option_chain = data
    #         else:
    #             self.msg_box.warning(self.msg_box, 'Error', 'No Option Found!', QMessageBox.Close, QMessageBox.Close)
    #             self.data_option_chain = pd.DataFrame({})
    #     else:
    #         self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)
    #         self.data_option_chain = pd.DataFrame({})
    #
    # def get_market_snapshot(self, security_code):
    #     ret, data = self.quote_ctx.get_market_snapshot([security_code])
    #     if ret == RET_OK:
    #         pass
    #     else:
    #         self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)
    #     return ret, data
    #
    # def position_list_query(self, code='', acc_id=0, acc_type=TrdEnv.REAL):
    #     self.trd_ctx_current.unlock_trade(self.pwd_unlock)
    #     ret, data = self.trd_ctx_current.position_list_query(code=code, trd_env=acc_type, acc_id=acc_id)
    #     if ret == RET_OK:
    #         if code == '':
    #             self.data_position_list = data
    #         else:
    #             return data
    #     else:
    #         self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)
    #
    # def order_list_query(self, code='', acc_id=0, acc_type=TrdEnv.REAL):
    #     self.trd_ctx_current.unlock_trade(self.pwd_unlock)
    #     ret, data = self.trd_ctx_current.order_list_query(code=code, trd_env=acc_type, acc_id=acc_id)
    #     if ret == RET_OK:
    #         if code == '':
    #             self.data_order_list = data
    #             self.sys_ord_mgr.total_update()
    #         else:
    #             return data
    #     else:
    #         self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)
    #
    # def historical_order_list_query(self, code='', acc_id=0, acc_type=TrdEnv.REAL):
    #     self.trd_ctx_current.unlock_trade(self.pwd_unlock)
    #     ret, data = self.trd_ctx_current.history_order_list_query(code=code, trd_env=acc_type, acc_id=acc_id)
    #     if ret == RET_OK:
    #         if code == '':
    #             self.data_historical_order_list = data
    #         else:
    #             return data
    #     else:
    #         self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)
    #
    # def deal_list_query(self, code='', acc_id=0, acc_type=TrdEnv.REAL):
    #     self.trd_ctx_current.unlock_trade(self.pwd_unlock)
    #     ret, data = self.trd_ctx_current.deal_list_query(code=code, trd_env=acc_type, acc_id=acc_id)
    #     if ret == RET_OK:
    #         if code == '':
    #             self.data_deal_list = data
    #         else:
    #             return data
    #     else:
    #         self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)
    #
    # def create_strategy(self, strategy, derivative, underlying, acc_id, acc_type):
    #     ret, strategy_instance = self.sys_stg_mgr.add_stg(strategy, derivative, underlying, acc_id, acc_type)
    #     if ret:
    #         if self.feed_subscribe(underlying) and self.feed_subscribe(derivative):
    #             # self.sys_stg_mgr.group_callback_orderbook(self.quote_ctx.get_order_book(underlying, 1)[1])
    #             # self.sys_stg_mgr.group_callback_orderbook(self.quote_ctx.get_order_book(derivative, 1)[1])
    #             strategy_instance.strategy_window.show()
    #         else:
    #             self.msg_box.warning(self.msg_box, 'Warning', "Subscription may not be successful!",
    #                                  QMessageBox.Close, QMessageBox.Close)
    #         return True
    #     else:
    #         return False
    #

    def feed_subscribe(self, security_code):
        ret_sub, err_message = self.quote_ctx.subscribe([security_code],
                                                        [SubType.ORDER_BOOK, SubType.TICKER],
                                                        is_first_push=True, extended_time=True)
        if ret_sub == RET_OK:
            self.shm.add_code(security_code)
            self.sys_log.log_out(['SYS'],
                                 'Subscribe Successfully:' + str(self.quote_ctx.query_subscription()))
            return True, err_message
        else:
            self.sys_log.log_out(['SYS', 'ERR'], str(err_message))
            return False, err_message

    #
    # def delete_strategy(self, derivative, underlying):
    #     if self.feed_unsubscribe(underlying):   # youwenti!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #         if self.feed_unsubscribe(derivative):
    #             self.sys_log.log_out("Try to delete strategy!")
    #             if self.sys_stg_mgr.del_stg(derivative, underlying):
    #                 return True
    #             else:
    #                 self.feed_subscribe(derivative)
    #                 self.feed_subscribe(underlying)
    #         else:
    #             self.feed_subscribe(underlying)
    #     return False
    #

    def feed_unsubscribe(self, security_code):
        ret_unsub, err_message_unsub = self.quote_ctx.unsubscribe([security_code],
                                                                  [SubType.ORDER_BOOK, SubType.TICKER])
        if ret_unsub == RET_OK:
            self.shm.del_code(security_code)
            self.sys_log.log_out(['SYS'],
                                 'Unsubscribe successfully！current subscription status:' + str(
                                     self.quote_ctx.query_subscription()))  # 取消订阅后查询订阅状态
            return True, err_message_unsub
        else:
            self.sys_log.log_out(['SYS', 'ERR'], 'Failed to cancel subscriptions！' + str(err_message_unsub))
            return False, err_message_unsub
    #
    # def callback_orderbook(self, data):
    #     self.sys_stg_mgr.group_callback_orderbook(data)
    #
    # def callback_ticker(self, data):
    #     self.sys_stg_mgr.group_callback_ticker(data)
    #
    # def callback_order(self, data):
    #     self.sys_ord_mgr.feed_update(data)
    #     self.sys_stg_mgr.group_callback_order(data)
    #
    # def callback_deal(self, data):
    #     self.sys_pos_mgr.feed_update(data)
    #     self.sys_stg_mgr.group_callback_deal(data)
    #
    # def create_order(self, strategy_instance, price, qty, side):  # better handover to OA
    #     if strategy_instance.region == 'US':
    #         self.trd_ctx_current = self.trd_ctx_us
    #     elif strategy_instance.region == 'HK':
    #         self.trd_ctx_current = self.trd_ctx_hk
    #     else:
    #         self.trd_ctx_current = self.trd_ctx_cn
    #     self.trd_ctx_current.unlock_trade(self.pwd_unlock)
    #     ret, data = self.trd_ctx_current.place_order(trd_env=strategy_instance.trading_type,
    #                                                  acc_id=strategy_instance.trading_account,
    #                                                  price=price,
    #                                                  qty=qty,
    #                                                  code=strategy_instance.derivative_code,
    #                                                  trd_side=side)
    #     if ret == RET_OK:
    #         self.sys_log.log_out("Order: " + str(data['order_id'][0]) + " has been sent! [" +
    #                              strategy_instance.derivative_code + "," +
    #                              str(strategy_instance.trading_account) + "," +
    #                              str(price) + "," +
    #                              str(qty) + "]"
    #                              )
    #     else:
    #         self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)
    #
    #     return ret, data
    #
    # def modify_order(self, order_id, acc_id, modifyorderop, qty=0, price=0):
    #     self.trd_ctx_current.unlock_trade(self.pwd_unlock)
    #     ret, data = self.trd_ctx_current.modify_order(modifyorderop,
    #                                                   order_id, qty, price,
    #                                                   trd_env=TrdEnv.REAL if int(
    #                                                       acc_id) > 99999999 else TrdEnv.SIMULATE,
    #                                                   acc_id=acc_id)
    #     if ret == RET_OK:
    #         if modifyorderop == ModifyOrderOp.CANCEL:
    #             self.sys_log.log_out("Order: " + str(data['order_id'][0]) + " has been canceled!")
    #         # print(data.to_dict())
    #     else:
    #         self.msg_box.warning(self.msg_box, 'Error', data, QMessageBox.Close, QMessageBox.Close)
    #     return ret, data
    #
    # def __del__(self):
    #     self.quote_ctx.close()
    #     self.trd_ctx_us.close()
    #     self.trd_ctx_hk.close()
    #     self.trd_ctx_cn.close()
    #
    #     sys.exit(self.app.exec_())
