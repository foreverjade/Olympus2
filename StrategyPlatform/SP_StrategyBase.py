class OptionStrategyBase:
    shm = None
    version = 'TestBaseSTG'

    def __init__(self, in_prod_list=None):
        self.prod_list = in_prod_list
        self.i_bidp1 = 0
        self.i_bidq1 = 0
        self.i_askp1 = 0
        self.i_askq1 = 0
        self.i_lasttrade_id = 0
        self.i_lasttradep = 0
        self.i_lasttradeq = 0
        self.i_lasttraded = False
        # self.f_update_time = 0

    # def set_prods(self, in_prod_list):
    #     self.prod_list = in_prod_list

    def on_mfh_callback(self, in_prod, in_istrade):
        if in_istrade:
            trade_idx = OptionStrategyBase.shm[in_prod]['trade_id']
            for i in range(self.i_lasttrade_id, trade_idx, 1):
                trade_subidx = str(i % 5)
                self.i_lasttradep = OptionStrategyBase.shm[in_prod]['trade_p' + trade_subidx]
                self.i_lasttradeq = OptionStrategyBase.shm[in_prod]['trade_q' + trade_subidx]
                self.i_lasttraded = OptionStrategyBase.shm[in_prod]['trade_d' + trade_subidx]
                print('[Trade] {};{};{}'.format(self.i_lasttradep, self.i_lasttradeq, self.i_lasttraded))
            self.i_lasttrade_id = trade_idx
        else:
            self.i_bidp1 = OptionStrategyBase.shm[in_prod]['bid_p1']
            self.i_bidq1 = OptionStrategyBase.shm[in_prod]['bid_q1']
            self.i_askp1 = OptionStrategyBase.shm[in_prod]['ask_p1']
            self.i_askq1 = OptionStrategyBase.shm[in_prod]['ask_q1']
            print('[Callback] {};{};{},{}'.format(self.i_bidp1, self.i_bidq1, self.i_askp1, self.i_askq1))
            pass
        # print(OptionStrategyBase.shm[in_prod])
