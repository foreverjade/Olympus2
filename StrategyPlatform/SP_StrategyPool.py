
class StrategyPool:
    shm = None
    cnn = None

    def __init__(self):
        self.prod_stg_map = {}
        self.stg_list = {}

    def add_stg(self, in_stg):
        str_name = "{}_{}".format(in_stg.version, len(self.stg_list))
        print('Add Stg: ', str_name)
        for prod in in_stg.prod_list:
            if prod in self.prod_stg_map:
                self.prod_stg_map[prod].append(str_name)
            else:
                self.prod_stg_map[prod] = [str_name]
        self.stg_list[str_name] = in_stg
        data = "1,SUBSCRIBE,US.TSLA220527C660000,1"
        StrategyPool.cnn.sendall(data.encode('utf-8'))
        print('send:', data)

    def print(self):
        print("prod_stg_map:", self.prod_stg_map)
        print("stg_list:", self.stg_list)