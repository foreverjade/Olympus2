from MarketFeedHandler.MFH_Constant import *
from SP_SharedMemory import *
from SP_Handler import *
from SP_StrategyPool import *
from SP_StrategyBase import *


class PlfCore:
    def __init__(self):

        self.shm = PlfShardMemory()
        StrategyPool.shm = self.shm
        OptionStrategyBase.shm = self.shm
        print('MFH ready!')

        self.mfh_conn = ClientSenderNewThread(self)
        self.mfh_conn.start()
        StrategyPool.cnn = self.mfh_conn.sock
        self.strategy_pool = StrategyPool()
        print('Conn ready!')

        self.strategy_pool.add_stg(OptionStrategyBase(['US.TSLA220527C660000']))
        # self.strategy_pool.print()

        time.sleep(2)
        # data = "1,SUBSCRIBE,US.TSLA220527C660000,1"
        # self.mfh_conn.sock.sendall(data.encode('utf-8'))
        # print('send:', data)
        time.sleep(20)
        data = "2,UNSUBSCRIBE,US.TSLA220527C660000,1"
        self.mfh_conn.sock.sendall(data.encode('utf-8'))
        print('send:', data)
        time.sleep(1)
        self.mfh_conn.sock.sendall('q'.encode('utf-8'))
        print('Sender closed!')
        self.mfh_conn.sock.close()

        self.mfh_conn.join()

    def data_communication(self, in_str):
        in_list = in_str.split(',')
        if in_list[IN_EVENT] == 'OBUPDATE':
            self.data_callback(in_list[IN_CODE], False)
        elif in_list[IN_EVENT] == 'TDUPDATE':
            self.data_callback(in_list[IN_CODE], True)
        elif in_list[IN_EVENT] == 'RESPONSE':
            self.shm.update()

    def data_callback(self, in_prod, in_istrade):
        for stg_name in self.strategy_pool.prod_stg_map[in_prod]:
            self.strategy_pool.stg_list[stg_name].on_mfh_callback(in_prod, in_istrade)
