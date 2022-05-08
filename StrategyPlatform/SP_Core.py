from MarketFeedHandler.MFH_Constant import *
from SP_SharedMemory import *
from SP_Handler import *


class PlfCore:
    def __init__(self):
        self.shm = PlfShardMemory()
        print('MFH ready!')
        self.mfh_conn = ClientSenderNewThread()
        self.mfh_conn.start()
        print('Conn ready!')
        self.mfh_conn.join()
