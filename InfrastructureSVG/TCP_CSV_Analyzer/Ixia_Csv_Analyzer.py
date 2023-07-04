import logging

from InfrastructureSVG.ProtocolSelector.protocol_selector import get_params


class IxiaCsvAnalyzer:
    def __init__(self, file, traffic_direction, count_from=0, results_and_status_obj=None, environment_objs=None, refactoring=False):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

        self.file = file
        self.traffic_direction = traffic_direction
        self.count_from = count_from
        self.refactoring = refactoring
        self.results_and_status_obj = results_and_status_obj
        self.environment_objs = environment_objs
        self.ixia_csv_analyzer()

    def ixia_csv_analyzer(self):
        protocol, dut, acp, dut_type = get_params(self.environment_objs)
        if self.file:
            if not self.results_and_status_obj.TEST_RESULTS[dut_type][self.environment_objs.tree[f'{dut}s_under_test'][1][acp]].get('total_tp'):
                self.results_and_status_obj.TEST_RESULTS[dut_type][self.environment_objs.tree[f'{dut}s_under_test'][1][acp]]['total_tp'] = {}
            if not self.results_and_status_obj.TEST_RESULTS[dut_type][self.environment_objs.tree[f'{dut}s_under_test'][1][acp]]['total_tp'].get(self.traffic_direction):
                self.results_and_status_obj.TEST_RESULTS[dut_type][self.environment_objs.tree[f'{dut}s_under_test'][1][acp]]['total_tp'][self.traffic_direction] = []
            for i in self.file[self.count_from:]:
                if 'ElapsedTime' in i[0]:
                    continue
                    # if 'UL' in self.traffic_direction and i[4] != '' and int(float(i[4])) / 1000 >= 1:  # float(i[4]) = 0
                # List extended with 2 same values because each row is per 2 minute
                if 'UL' in self.traffic_direction and i[4] != '':
                    self.results_and_status_obj.TEST_RESULTS[dut_type][self.environment_objs.tree[f'{dut}s_under_test'][1][acp]]['total_tp'][self.traffic_direction].extend(
                        (float("%.2f" % (float(i[4]) / 1000)), float("%.2f" % (float(i[4]) / 1000))))
                elif 'DL' in self.traffic_direction and i[2] != '':  # float(i[2]) = 0
                    self.results_and_status_obj.TEST_RESULTS[dut_type][self.environment_objs.tree[f'{dut}s_under_test'][1][acp]]['total_tp'][self.traffic_direction].extend(
                        (float("%.2f" % (float(i[2]) / 1000)), float("%.2f" % (float(i[2]) / 1000))))
            self.update_tp_results()
        else:
            self.logger.warning('file parameter is empty')

    def update_tp_results(self):
        protocol, dut, acp, dut_type = get_params(self.environment_objs)
        final_list = self.results_and_status_obj.TEST_RESULTS[dut_type][self.environment_objs.tree[f'{dut}s_under_test'][1][acp]]['total_tp'][self.traffic_direction]
        self.results_and_status_obj.TEST_RESULTS[dut_type][self.environment_objs.tree["dus_under_test"][1]["gnb_acp_name"]]['tp_results'].update(
            {
                f'{self.traffic_direction}MinRxRate(Mbps)': float('%.1f' % min(final_list)) if final_list else 0,
                f'{self.traffic_direction}AvgRxRate(Mbps)': float('%.1f' % (sum(final_list) / len(final_list)) if final_list else 0),
                f'{self.traffic_direction}MaxRxRate(Mbps)': float('%.1f' % max(final_list) if final_list else 0)
            }
        )
