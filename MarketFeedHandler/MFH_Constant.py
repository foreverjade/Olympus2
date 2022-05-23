import numpy as np

# FILE PATH
PROJECT_PATH = "C:/Users/shrfa/PycharmProjects/pythonProject/"
MFH_FOLDER = "MarketFeedHandler/"
SP_FOLDER = "StrategyPlatform/"

# MFH WEB SETTING
MFH_IP = '127.0.0.1'
MFH_PORT = 11111
MFH_SOCKET_PORT = 22222
BUFF_SIZE = 1024

# FUTU ACCT SETTING
FUTU_UNLOCK = '900213'

# MFH DATA STRUCT STANDARDS
MFH_CAPACITY = 100
MFH_DEF_LINE = np.array([(False, 0)],
                        dtype=[('mfh_update', 'b'), ('used_slot', 'i2')])
ORDER_BOOK_LINE = np.array([('CODE', '', '', False, 0.0, 0, 0, 0.0, 0, 0, '', 0,
                             0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False, 0, 0, False)],
                           dtype=[('code', 'U24'), ('timestamp_bid', 'U24'), ('timestamp_ask', 'U24'), ('log', 'b'),
                                  ('bid_p1', 'i4'), ('bid_q1', 'i4'), ('bid_c1', 'i4'),
                                  ('ask_p1', 'i4'), ('ask_q1', 'i4'), ('ask_c1', 'i4'),
                                  ('timestamp_lasttrade', 'U24'), ('trade_id', 'i4'),
                                  ('trade_p0', 'i4'), ('trade_q0', 'i4'), ('trade_d0', 'b'),
                                  ('trade_p1', 'i4'), ('trade_q1', 'i4'), ('trade_d1', 'b'),
                                  ('trade_p2', 'i4'), ('trade_q2', 'i4'), ('trade_d2', 'b'),
                                  ('trade_p3', 'i4'), ('trade_q3', 'i4'), ('trade_d3', 'b'),
                                  ('trade_p4', 'i4'), ('trade_q4', 'i4'), ('trade_d4', 'b')
                                  ])
PRICE_ADJ = 1000

# COMMUNICATION STANDARDS
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
