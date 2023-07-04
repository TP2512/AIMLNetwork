import os
import re

from InfrastructureSVG.Files_Infrastructure.Folders.Path_folders_Infrastructure import GeneralFolderActionClass


class CoreFinder:
    def __init__(self):
        self.core = []

    def extract_core(self, path):
        path_validator = GeneralFolderActionClass()
        if path_validator.check_path_exist(path):
            for file in os.listdir(path):
                if 'under_test_corecare' in file:
                    with open(f"{path}\\{file}", "r") as data:
                        lines = data.read()
                        cores = re.findall(r'dumping core file /var/crash/(.*)', lines)
                        self.core += [i.replace('gz', 'tgz') for i in cores]

        return self.core


if __name__ == "__main__":
    url = '\\\\192.168.127.231\\AutomationResults\\old_runs\\ASIL-SATURN\\5117\\RobotFrameworkSVG\\Test_Logs_And_Files\\SIR-38337\\gnb_1_ED085B0164EC\\XPU'
    core = CoreFinder().extract_core(url)
    print(core)
