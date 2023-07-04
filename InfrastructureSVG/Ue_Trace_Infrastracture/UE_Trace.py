from InfrastructureSVG.Network_Infrastructure.websocket_Infrastructure import WebSocketActions
import asyncio
import paramiko
import pickle
import pyshark
import os


class Analyze_Pcap:
    def __init__(self):
        self.remote_path = "/home/spuser/pcaps/"
        self.server = "192.168.127.9"
        self.port = '8000'
        self.username = "spuser"
        self.password = "sp_user9"
        self.finale_packets = None

    async def listen(self, pcap_name):
        return pickle.loads(await WebSocketActions(web_socket_ip_address=self.server, web_socket_port=self.port).async_send_params(self.remote_path + pcap_name))

    def file_transfer(self, path_from):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=self.server, username=self.username, password=self.password)
        sftp = ssh_client.open_sftp()
        file_name = path_from.split("\\")[-1]
        sftp.put(path_from, f"{self.remote_path}{file_name}")
        sftp.close()
        return file_name

    def get_packets(self, directory):
        if os.path.exists(directory):
            name = self.file_transfer(directory)
            self.finale_packets = asyncio.run(self.listen(name))
            return asyncio.run(self.listen(name))
        raise SystemError('Incorrect Path,\n File was not found')

    def get_num_of_events(self):
        num_packets = {"uu": 0, "ngap": 0, "xn": 0, "ng": 0}
        for package in self.finale_packets:
            if "RRC" in package['Event type'] or "VENDOR" in package['Event type']:
                num_packets["uu"] += 1
            elif "NGAP" in package['Event type']:
                num_packets["ngap"] += 1
            elif "Xn" in package['Event type']:
                num_packets["xn"] += 1
            elif "Ng" in package['Event type']:
                num_packets["ng"] += 1
        return num_packets

    def check_trace_pcap(self, pcap_path: str, expected: dict, reps):
        self.get_packets(pcap_path)
        copy_expected = expected
        for interface in copy_expected:
            copy_expected[interface] = copy_expected[interface] * int(reps)
        return self.return_errors(copy_expected)

    def return_errors(self, desired=None):
        act_results = self.get_num_of_events()
        unexpected = []
        over = []
        under = []
        for interface in desired:
            if desired[interface] == 0 and act_results[interface] > 0 and interface != "ngap":
                unexpected.append(interface)
            elif act_results[interface] < desired[interface]:
                under.append(interface)
            elif act_results[interface] > desired[interface]:
                over.append(interface)
        if unexpected:
            return False, act_results, f"{', '.join(unexpected)} were not expected in this test"
        elif under:
            return False, act_results, f"{', '.join(under)} were found with less packets than expected"
        elif over:
            return True, act_results, f"warning; {', '.join(over)} were found with more packets than expected"
        else:
            return True, act_results, None

    def get_results(self, pcap_path):
        self.get_packets(pcap_path)
        return self.get_num_of_events()


if __name__ == "__main__":
    inst = Analyze_Pcap()
    status, results, failure = inst.check_trace_pcap(r"C:\Users\ashachar\Desktop\latest_amit.pcap",
                                                     {"uu": 2, "xn": 2, "ngap": 0, "ng": 0}, "4")
    # print((status, results, failure))
    inst.get_results(r"C:\Users\ashachar\Desktop\latest_amit.pcap")
    print()
