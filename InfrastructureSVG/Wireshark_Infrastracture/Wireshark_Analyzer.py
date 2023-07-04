import pyshark
import os


class WiresharkAnalayzer:

    @staticmethod
    def read_pcap(pcap_path):
        if os.path.isfile(pcap_path):
            return list(pyshark.FileCapture(pcap_path))
        return False

    def get_inverse_pcap(self, pcap_path):
        pcap = self.read_pcap(pcap_path)
        return pcap[::-1]


if __name__ == "__main__":
    instance = WiresharkAnalayzer()
    packets = instance.get_inverse_pcap(
        "C:\\Users\\ashachar\\Downloads\\ue_inactivity_udp.pcap")
    print()
