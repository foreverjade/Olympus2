from MFH_Constant import *
from multiprocessing import shared_memory

'''

OrderBookTest  {'code': 'HK.00700', 'svr_recv_time_bid': '2020-04-29 15:55:53.299', 'svr_recv_time_ask': '2020-04-29 15:55:53.299', 'Bid': [(414.2, 60600, 63, {}), (414.0, 96000, 34, {}), (413.8, 23400, 17, {}), (413.6, 31800, 24, {}), (413.4, 33900, 19, {}), (413.2, 47800, 17, {}), (413.0, 42500, 44, {}), (412.8, 17000, 6, {}), (412.6, 10600, 6, {}), (412.4, 5200, 5, {})], 'Ask': [(414.4, 74200, 61, {}), (414.6, 25700, 26, {}), (414.8, 18800, 24, {}), (415.0, 35700, 51, {}), (415.2, 17500, 15, {}), (415.4, 33500, 9, {}), (415.6, 62000, 18, {}), (415.8, 36700, 11, {}), (416.0, 42000, 73, {}), (416.2, 3800, 10, {})]}
'''


class SysShardMemory:
    sys_log = None

    def __init__(self, p_core):
        self.link_core = p_core
        self.code_map = {}
        self.shm = shared_memory.SharedMemory(name='MFH', create=True,
                                              size=MFH_DEF_LINE.nbytes + ORDER_BOOK_LINE.nbytes * MFH_CAPACITY)
        self.definition = np.ndarray((1,), dtype=MFH_DEF_LINE.dtype, buffer=self.shm.buf)
        self.trade_tables = np.ndarray((MFH_CAPACITY,), dtype=ORDER_BOOK_LINE.dtype, buffer=self.shm.buf,
                                       offset=MFH_DEF_LINE.nbytes)

    def used_size(self):
        return len(self.code_map)

    def find_id(self):
        for i in range(len(self.code_map)):
            x = list(self.code_map.values())
            x.sort()
            if x[i] != i:
                return i
        else:
            return len(self.code_map)

    def add_code(self, in_code):
        if in_code not in self.code_map:
            code_map_id = self.find_id()
            self.trade_tables['code'][code_map_id] = in_code
            self.code_map[in_code] = code_map_id
            self.__dict__[in_code] = self.trade_tables[code_map_id]
            # print('========add code:', in_code)
            # print('========in_code:', self.__dict__[in_code]['code'])
            self.definition['mfh_update'][0] = True
            self.definition['used_slot'][0] = self.used_size()
            self.link_core.sys_log.log_out(['SYS', 'SHM'],
                                           'Shared Memory code added: ' + in_code + '; Capacity: ' + str(
                                               self.definition['used_slot'][0]) + '/' + str(MFH_CAPACITY))
            return True
        else:
            self.link_core.sys_log.log_out(['SYS', 'SHM'], 'Shared Memory code already exists: ' + in_code)
            return False

    def del_code(self, in_code):
        if in_code in self.code_map:
            del self.code_map[in_code]
            del self.__dict__[in_code]
            self.definition['mfh_update'][0] = True
            self.definition['used_slot'][0] = self.used_size()
            self.link_core.sys_log.log_out(['SYS', 'SHM'],
                                           'Shared Memory code deleted: ' + in_code + '; Capacity: ' + str(
                                               self.definition['used_slot'][0]) + '/' + str(MFH_CAPACITY))
            return True
        else:
            self.link_core.sys_log.log_out(['SYS', 'SHM'], 'Shared Memory code does not exists: ' + in_code)
            return False

    def __getitem__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        else:
            return None

    def close(self):
        self.shm.close()
        self.shm.unlink()
