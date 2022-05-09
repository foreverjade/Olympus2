from MFH_Constant import *

from datetime import *
import os
import threading



#
# class SysStrategyManager:
#     def __init__(self, p_core):
#         self.link_core = p_core
#         self.l_derivatives = []
#         self.l_underlyings = []
#         self.l_objects = []
#         self.dict_dev2objects = {}
#         self.dict_ul2objects = {}
#         self.dict_ul2dev = {}
#         self.stg_count = 0
#
#     def add_stg(self, strategy, derivative, underlying, acc_id, acc_type):
#         new_stg = None
#         if derivative in self.dict_dev2objects:
#             self.dict_dev2objects[derivative].strategy_window.show()
#             self.link_core.sys_log.log_out("Already has strategy for " + derivative)
#         else:
#             if strategy == 'RuleUSOptionManual':
#                 new_win = FormStrategyTrading(self.link_core.olympusWin, derivative)
#                 new_stg = RuleUSOptionManual(derivative, underlying, self.link_core, new_win, acc_id, acc_type)
#                 new_win.strategy_instance = new_stg
#                 new_win.status_check()
#
#             else:
#                 pass
#
#             if new_stg is not None:
#                 # update list
#                 self.l_derivatives.append(derivative)
#                 self.link_core.sys_log.log_out("Update derivative list:" + str(self.l_derivatives))
#                 if underlying not in self.l_underlyings:
#                     self.l_underlyings.append(underlying)
#                     self.link_core.sys_log.log_out("Update underlying list:" + str(self.l_underlyings))
#                 self.l_objects.append(new_stg)
#                 self.link_core.sys_log.log_out("Update objects list:" + str(self.l_objects))
#                 # update dict
#                 self.dict_dev2objects[derivative] = new_stg
#                 self.link_core.sys_log.log_out("Update dev2objects dict:" + str(self.dict_dev2objects))
#                 if underlying not in self.dict_ul2objects:
#                     self.dict_ul2objects[underlying] = []
#                 self.dict_ul2objects[underlying].append(new_stg)
#                 self.link_core.sys_log.log_out("Update ul2objects dict:" + str(self.dict_ul2objects))
#                 if underlying not in self.dict_ul2dev:
#                     self.dict_ul2dev[underlying] = []
#                 if derivative not in self.dict_ul2dev[underlying]:
#                     self.dict_ul2dev[underlying].append(derivative)
#                     self.link_core.sys_log.log_out("Update ul2dev dict:" + str(self.dict_ul2dev))
#             self.stg_count += 1
#             self.link_core.sys_log.log_out("Strategy Created: " + derivative)
#             return True, new_stg
#         return False, None
#
#     def del_stg(self, derivative, underlying):
#         if derivative in self.l_derivatives:
#             p_del = self.dict_dev2objects.pop(derivative)
#             self.link_core.sys_log.log_out("Update dev2objects dict:" + str(self.dict_dev2objects))
#             p_del = self.dict_ul2objects[underlying].pop(self.dict_ul2objects[underlying].index(p_del))
#             if len(self.dict_ul2objects[underlying]) == 0:
#                 del self.dict_ul2objects[underlying]
#             self.link_core.sys_log.log_out("Update ul2objects dict:" + str(self.dict_ul2objects))
#             self.dict_ul2dev[underlying].pop(self.dict_ul2dev[underlying].index(derivative))
#             if len(self.dict_ul2dev[underlying]) == 0:
#                 del self.dict_ul2dev[underlying]
#             self.link_core.sys_log.log_out("Update ul2dev dict:" + str(self.dict_ul2dev))
#             p_del = self.l_objects.pop(self.l_objects.index(p_del))
#             self.link_core.sys_log.log_out("Update objects list:" + str(self.l_objects))
#             p_del.delete()
#             self.l_derivatives.pop(self.l_derivatives.index(derivative))
#             self.link_core.sys_log.log_out("Update derivatives list:" + str(self.l_derivatives))
#             if underlying not in self.dict_ul2dev:
#                 self.l_underlyings.pop(self.l_underlyings.index(underlying))
#                 self.link_core.sys_log.log_out("Update underlying list:" + str(self.l_underlyings))
#             self.stg_count -= 1
#             self.link_core.sys_log.log_out("Strategy Deleted: " + derivative)
#             return True
#         else:
#             self.link_core.sys_log.log_out("No strategy exists for " + derivative)
#             return False
#
#     def is_empty(self):
#         return self.stg_count > 0
#
#     def group_callback_orderbook(self, data):
#         if len(data['code']) > 16:
#             self.dict_dev2objects[data['code']].on_feed(data, RuleBase.FEED_DERI_QUOTE)
#         else:
#             for ob in self.dict_ul2objects[data['code']]:
#                 ob.on_feed(data, RuleBase.FEED_UL_QUOTE)
#
#     def group_callback_ticker(self, data):
#         for i in range(len(data)):
#             if len(data['code'][i]) > 16:
#                 self.dict_dev2objects[data['code'][i]].on_feed(data.loc[i, :], RuleBase.FEED_DERI_TRADE)
#             else:
#                 for ob in self.dict_ul2objects[data['code'][i]]:
#                     ob.on_feed(data.loc[i, :], RuleBase.FEED_UL_TRADE)
#
#     def group_callback_order(self, data):
#         for i in range(len(data)):
#             if data['code'][i] in self.dict_dev2objects:
#                 self.dict_dev2objects[data['code'][i]].on_feed(data.loc[data.index == i, :], RuleBase.FEED_ORDER)
#
#     def group_callback_deal(self, data):
#         print("group_callback_deal: " + str(data.to_dict('list')))
#         for i in range(len(data)):
#             if data['code'][i] in self.dict_dev2objects:
#                 self.dict_dev2objects[data['code'][i]].on_feed(data.loc[data.index == i, :], RuleBase.FEED_DEAL)
#
#
# class SysPositionManager:
#     def __init__(self, p_core):
#         self.link_core = p_core
#         self.dict_dev2position = {}
#
#     def total_update(self):
#         df_position = self.link_core.data_position_list
#         for i in df_position.index:
#             if df_position.at[i, 'code'] not in self.dict_dev2position:
#                 self.dict_dev2position[df_position.at[i, 'code']] = [df_position.at[i, 'qty'],
#                                                                      df_position.at[i, 'can_sell_qty'],
#                                                                      df_position.at[i, 'cost_price'],
#                                                                      df_position.at[i, 'pl_val'],
#                                                                      df_position.at[i, 'today_val']]
#
#     def feed_update(self, data):  # order data
#         # if data['order_status'][0] == OrderStatus.FILLED_PART or OrderStatus.FILLED_ALL:
#         #     delta_qty = data['qty'][0] if data['trd_side'][0] == TrdSide.BUY else 0 - data['qty'][0]
#         #     if data['code'][0] not in self.dict_dev2position:
#         #         self.dict_dev2position[data['code'][0]] = [
#         #             delta_qty,
#         #             data['qty'][0],
#         #             data['dealt_avg_price'][0],
#         #             0,
#         #             0]
#         #     else:
#         #         origin_qty = self.dict_dev2position[data['code'][0]][0]
#         #         origin_cost = self.dict_dev2position[data['code'][0]][2]
#         #         self.dict_dev2position[data['code'][0]][0] += delta_qty
#         #         self.dict_dev2position[data['code'][0]][1] += delta_qty
#         #         self.dict_dev2position[data['code'][0]][2] = \
#         #             ((origin_qty * origin_cost) + (delta_qty * data['dealt_avg_price'][0])) / (origin_qty + delta_qty)
#         #         if origin_qty * delta_qty < 0:
#         #             self.dict_dev2position[data['code'][0]][3] += delta_qty * (origin_cost - data['dealt_avg_price'][0])
#         #             self.dict_dev2position[data['code'][0]][4] += delta_qty * (origin_cost - data['dealt_avg_price'][0])
#         pass
#
#
# class SysOrderManager:
#     def __init__(self, p_core):
#         self.link_core = p_core
#         self.dict_orders = {}
#         self.dict_dev2orders = {}
#         self.status_filter_list = [OrderStatus.CANCELLED_ALL, OrderStatus.DELETED]
#
#     def total_update(self):
#         df_orders = self.link_core.data_order_list
#         for i in df_orders.index:
#             if df_orders.at[i, 'order_status'] in self.status_filter_list:
#                 continue
#             if df_orders.at[i, 'code'] not in self.dict_dev2orders:
#                 self.dict_dev2orders[df_orders.at[i, 'code']] = []
#             if df_orders.at[i, 'order_id'] not in self.dict_dev2orders[df_orders.at[i, 'code']]:
#                 self.dict_dev2orders[df_orders.at[i, 'code']].append(df_orders.at[i, 'order_id'])
#             if df_orders.at[i, 'order_id'] not in self.dict_orders:
#                 self.dict_orders[df_orders.at[i, 'order_id']] = (df_orders.at[i, 'code'],
#                                                                  df_orders.at[i, 'trd_side'],
#                                                                  df_orders.at[i, 'order_type'],
#                                                                  df_orders.at[i, 'order_status'],
#                                                                  df_orders.at[i, 'qty'],
#                                                                  df_orders.at[i, 'price'],
#                                                                  df_orders.at[i, 'create_time'])
#
#     def feed_update(self, data):
#         if data['order_status'][0] not in self.status_filter_list:
#             if data['code'][0] in self.link_core.sys_stg_mgr.dict_dev2objects:
#                 win = self.link_core.sys_stg_mgr.dict_dev2objects[data['code'][0]].strategy_window
#                 win.signal_order_update.emit(data, 0)
#             if data['code'][0] not in self.dict_dev2orders:
#                 self.dict_dev2orders[data['code'][0]] = []
#             if data['order_id'][0] not in self.dict_dev2orders[data['code'][0]]:
#                 self.dict_dev2orders[data['code'][0]].append(data['order_id'][0])
#             if data['order_id'][0] not in self.dict_orders:
#                 self.dict_orders[data['order_id'][0]] = (data['code'][0],
#                                                          data['trd_side'][0],
#                                                          data['order_type'][0],
#                                                          data['order_status'][0],
#                                                          data['qty'][0],
#                                                          data['price'][0],
#                                                          data['create_time'][0])
#         else:
#             if data['code'][0] in self.link_core.sys_stg_mgr.dict_dev2objects:
#                 win = self.link_core.sys_stg_mgr.dict_dev2objects[data['code'][0]].strategy_window
#                 win.signal_order_update.emit(data, 1)
#             self.dict_orders.pop(data['order_id'][0])
#             self.dict_dev2orders[data['code'][0]].pop(
#                 self.dict_dev2orders[data['code'][0]].index(data['order_id'][0]))
#             if len(self.dict_dev2orders[data['code'][0]]) == 0:
#                 self.dict_dev2orders.pop(data['code'][0])
#


class SysFeedManager:
    def __init__(self):
        # self.client_prod_map = {("127.0.0.1", 53307): ["US.APPL"]}
        # self.prod_client_map = {"US.APPL": [("127.0.0.1", 53307)]}
        # self.client_request_map = {("127.0.0.1", 53307): queue[msg1,msg2,...]}
        self.client_prod_map = {}
        self.prod_client_map = {}
        self.client_request_map = {}

    def add_pair(self, in_client_prod_pair):
        client = in_client_prod_pair[0]
        prod = in_client_prod_pair[1]
        if client in self.client_prod_map:
            if prod not in self.client_prod_map[client]:
                self.client_prod_map[client].append(prod)
        else:
            self.client_prod_map[client] = [prod]
        if prod in self.prod_client_map:
            if client not in self.prod_client_map[prod]:
                self.prod_client_map[prod].append(client)
        else:
            self.prod_client_map[prod] = [client]

    def del_pair(self, in_client_prod_pair):
        client = in_client_prod_pair[0]
        prod = in_client_prod_pair[1]
        if client in self.client_prod_map:
            if prod in self.client_prod_map[client]:
                self.client_prod_map[client].remove(prod)
                if len(self.client_prod_map[client]) == 0:
                    del self.client_prod_map[client]
        if prod in self.prod_client_map:
            if client in self.prod_client_map[prod]:
                self.prod_client_map[prod].remove(client)
                if len(self.prod_client_map[prod]) == 0:
                    del self.prod_client_map[prod]

    def del_client(self, in_client):
        if in_client in self.client_prod_map:
            del self.client_prod_map[in_client]
        del_list =[]
        for prod in self.prod_client_map:
            if in_client in self.prod_client_map[prod]:
                self.prod_client_map[prod].remove(in_client)
                if len(self.prod_client_map[prod]) == 0:
                    del_list.append(prod)
        for prod in del_list:
            del self.prod_client_map[prod]
        if in_client in self.client_request_map:
            del self.client_request_map[in_client]


class SysFileManager:
    def __init__(self, p_core):
        self.link_core = p_core
        # file path
        date_str = datetime.now().strftime("%Y%m%d")
        path_data = PROJECT_PATH + MFH_FOLDER + "Data/" + date_str + "/"
        folder = os.path.exists(path_data)
        if not folder:
            os.makedirs(path_data)
        self.file_quote_handler_output = open(path_data + date_str + "_QUOTE_DATA.csv", mode='a+')
        self.file_quote_handler_output.write('TIMEBID,TIMEASK,CODE,BID_P1,BID_Q1,BID_C1,ASK_P1,ASK_Q1,ASK_C1\n')
        self.file_ticker_handler_output = open(path_data + date_str + "_TICKER_DATA.csv", mode='a+')
        self.file_ticker_handler_output.write('TIME,CODE,PRICE,QTY,SIDE\n')
        self.file_order_handler_output = open(path_data + date_str + "_ORDER_DATA.csv", mode='a+')
        self.file_deal_handler_output = open(path_data + date_str + "_DEAL_DATA.csv", mode='a+')

        path_log = PROJECT_PATH + MFH_FOLDER + "Logs/"
        self.file_sys_log_output = open(path_log + date_str + "_SYS_LOG.log", encoding='utf-8', mode='a+')

    def update(self):
        pass

    def __del__(self):
        self.file_quote_handler_output.close()
        self.file_ticker_handler_output.close()
        self.file_order_handler_output.close()
        self.file_deal_handler_output.close()
        self.file_sys_log_output.close()
