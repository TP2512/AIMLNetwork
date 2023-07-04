import os
import subprocess
import json
import datetime
import traceback as tb
from inspect import currentframe, getframeinfo
import logging

from InfrastructureSVG.Files_Infrastructure.Log_Analyzer.tracking.Logger import Logger


class ASN1Parse:
    def __init__(self):
        self.logger = Logger()
        self.asn_file_path = os.path.realpath(
            os.path.join(
                os.path.dirname(__file__),
                '3GPP F1AP v15.3.0.asn'))
        self.asn1step_executable = os.path.realpath(
            r"C:\Program Files\OSS Nokalva\asn1step\winx64.trial\10.1.1\bin\asn1step.exe")
        self.per_file_path = os.path.realpath(
            os.path.join(os.path.dirname(__file__), 'F1AP-PDU.per'))
        self.json_file_path = os.path.realpath(os.path.join(
            os.path.dirname(__file__), 'F1AP-PDU.per.json'))

    def store_hex(self, hex_str):
        with open(self.per_file_path, "w") as per_file:
            per_file.write(hex_str)

    def parse(self, hex_str):
        self.store_hex(hex_str)
        subprocess.run([self.asn1step_executable,
                        self.asn_file_path,
                        '-root',
                        '-decodePdu',
                        'F1AP-PDU',
                        self.per_file_path,
                        '-hex',
                        '-json'], shell=True, stdout=subprocess.PIPE)
        try:
            json_o = self.get_json_string()
        except Exception:
            json_o = None
            frame_info = getframeinfo(currentframe())
            track_message = f"can't get ASN1 json string."
            self.logger.error(frame_info, track_message)
        return json_o

    def get_json_string(self):
        with open(self.json_file_path, "r") as json_file:
            json_hex = json_file.read()
            json_str = bytearray.fromhex(json_hex).decode()
            json_o = json.loads(json_str)
            return json_o

    def find_all_json_keys(self, key, dictionary):
        for k, v in dictionary.items():
            if k == key:
                yield v
            elif isinstance(v, dict):
                for result in self.find_all_json_keys(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in self.find_all_json_keys(key, d):
                        yield result


if __name__ == "__main__":
    asn1Parse = ASN1Parse()
    json_ob = asn1Parse.parse(
        '00030080c1000003004e00020002003e00809f0000003d0080984000f19500000000140000f1950000000010000b0000010800f1950000008340040'
        '0000020410009c12000004d002e000100000379cd2c606c8300a340410012c800000800000000c0280c0150e116219a421340600000c418d6d8d7f4'
        'a6e080400001010000800d1808509098c0840000621ab8d6d8da9280321c19aeb285200498e129c35388a7154cdc000263a010580e0020729180200'
        '059001000010058000a0000f195000000001000')
