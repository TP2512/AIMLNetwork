class ReturnChipset:
    def __init__(self):
        self.chipset_list_17_50 = ['FSMv3', 'FSMv4', 'XLP']
        self.chipset_list_17_00 = ['FSMv3', 'XLP']
        self.chipset_list_rakuten = ['DU-FSM', 'DU-XLP']

    def return_chipset_list(self, version):
        if '17.50' in version.version:
            return self.chipset_list_17_50
        elif version.is_rakuten:
            return self.chipset_list_rakuten
        return self.chipset_list_17_00
