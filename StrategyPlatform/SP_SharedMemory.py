from MarketFeedHandler.MFH_Constant import *
from multiprocessing import shared_memory
from SP_StrategyBase import *


class PlfShardMemory:
    plf_log = None

    def __init__(self):
        self.code_map = {}
        self.shm = shared_memory.SharedMemory(name='MFH')
        self.definition = np.ndarray((1,), dtype=MFH_DEF_LINE.dtype, buffer=self.shm.buf)
        self.trade_tables = np.ndarray((MFH_CAPACITY,), dtype=ORDER_BOOK_LINE.dtype, buffer=self.shm.buf,
                                       offset=MFH_DEF_LINE.nbytes)
        self.update()

    def update(self):
        for ele in self.code_map.keys():
            del self.__dict__[ele]
        self.code_map.clear()
        for i in range(self.definition['used_slot'][0]):
            self.code_map[self.trade_tables['code'][i]] = i
            self.__dict__[self.trade_tables['code'][i]] = self.trade_tables[i]

    def __getitem__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        else:
            return None
