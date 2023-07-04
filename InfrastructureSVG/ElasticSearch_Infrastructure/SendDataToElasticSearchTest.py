from InfrastructureSVG.ElasticSearch_Infrastructure.ElasticSearchConnection import ElasticSearchConnection
from datetime import datetime, timezone

if __name__ == '__main__':
    statuses = ['PASS', 'FAIL']
    features = ['UDP PTP UpLink', 'UDP PTP DownLink', 'UDP PTP BiDirectional', 'UDP PT2P UpLink', 'UDP PT2P DownLink', 'UDP PT2P BiDirectional']
    cu_versions = ['19.00-7-0.0', '19.00-6-0.0', '19.00-5-0.0']
    hw_types = [['AirVelocity 2700', 'AirVelocity 2700'], ['AirVelocity 2200', 'AirVelocity 2200']]
    bands = ['n71', 'n78']
    bws = ['20Mhz', '100Mhz']
    dls = [450, 455, 459, 350]
    uls = [56, 60, 45, 40]

    client = ElasticSearchConnection().connect_to_svg_elasticsearch()

    for status in statuses:
        for feature in features:
            for cu_version in cu_versions:
                for hw_type in hw_types:
                    for band in bands:
                        for bw in bws:
                            for dl in dls:
                                for ul in uls:
                                    doc = {
                                        'BSHardwareType': hw_type,
                                        "Automation Setup Name": 'ASIL-Toyota',
                                        "Band": band,
                                        'BW': bw,
                                        'Numerology(SCS)': 'Numerology=1,SCS=30Khz',
                                        'Format(SSF)': 'Format 2 - DL 0% : UL 0%',
                                        'DL Layers': 2,
                                        'UL Layers': 1,
                                        'Test Plan': 'SVGA-13',
                                        'Automation Test Set Key': 'SIR-39068',
                                        'G5_CUCP_Ver': cu_version,
                                        'G5_CUUP_Ver': cu_version,
                                        'G5_DU_Ver': '19.00-23-0.0',
                                        'G5_RU_Ver': 'AS-AV27-R1.5.11',
                                        'Test_Run_Time': 300,
                                        'Netspan and SF SW Version': '129.19.00.011',
                                        'Path': 'file://///ASIL-Toyota/RobotFrameworkSVG/872/Test_Logs_And_Files/SIR-37167',
                                        'DL Throughput (Mbps)': dl,
                                        'UL Throughput (Mbps)': ul,
                                        'Traffic Transport Layer Protocol': 'TCP',
                                        'Automation Traffic Direction': 'DL',
                                        'Traffic Testing tool': 'IXIA',
                                        'Link': 'https://tinyurl.com/ygzuozxo',
                                        'Test SIR': 'SIR-38928',
                                        'Execution Summary': '[IXIA]TCP TP PT2P - UL only - 1 Hour (SIR-38928) executed by Jenkins (874)',
                                        'Labels': ['Build_874', 'IXIA', 'Throughput'],
                                        'Fix Version/s': 'SR19_0_SVG_Weekly_Regression',
                                        'Test Status': status,
                                        'Environment Config': None,
                                        'Execution Key': 'SVGA-146',
                                        'Core Occurrence count': 0,
                                        'Core SystemUpTime (min)': 0,
                                        'Feature Name': feature,
                                        'timestamp': datetime.now(timezone.utc),
                                    }

                                    client.index(index='automationresultstest', body=doc)
    print()
