gnb_type = 'AIO'

# fix_version = '19.00'
# fix_version = '19.50'
fix_version = 'All'

if fix_version == '19.00':
    version_list = ['19.00-130-4.1', '19.00-130-4.2', '19.00-130-4.3', '19.00-130-4.4', '19.00-130-4.5']
    ems_version_list = ['19.00-10-1.1', '19.00-10-1.2', '19.00-10-1.3', '19.00-10-1.4', '19.00-10-1.5']
elif fix_version == '19.50':
    version_list = ['19.50-562-9.1', '19.50-562-9.2', '19.50-562-9.3', '19.50-562-9.4', '19.50-562-9.5']
    ems_version_list = ['19.50-90-1.1', '19.50-90-1.2', '19.50-90-1.3', '19.50-90-1.4', '19.50-90-1.5']
else:
    version_list = [
        '19.00-130-4.1', '19.00-130-4.2', '19.00-130-4.3', '19.00-130-4.4', '19.00-130-4.5',
        '19.50-562-9.1', '19.50-562-9.2', '19.50-562-9.3', '19.50-562-9.4', '19.50-562-9.5',
    ]
    ems_version_list = [
        '19.00-10-1.1', '19.00-10-1.2', '19.00-10-1.3', '19.00-10-1.4', '19.00-10-1.5',
        '19.50-90-1.1', '19.50-90-1.2', '19.50-90-1.3', '19.50-90-1.4', '19.50-90-1.5'
    ]

slave_name_list = ['ASIL-AZAGURI-1', 'ASIL-AZAGURI-2', 'ASIL-AZAGURI-3', 'ASIL-AZAGURI-4', 'ASIL-AZAGURI-5']

gnbs_configuration_list = [
    {
        '1': {
            'gnb_number': '1',
            'hardware': 'AirSpeed_2200/AirSpeed_2200',
            'band': 'n48',
            'bw': '20+20MHz',
            'numerology': '1',
            'scs': '10Khz',
            'imsi': 200010001234561
        },
        '2': {
            'gnb_number': '2',
            'hardware': 'AirSpeed_2200/AirSpeed_2200',
            'band': 'n48',
            'bw': '20MHz',
            'numerology': '1',
            'scs': '20Khz',
            'imsi': 200010001234562
        }
    },
    {
        '1': {
            'gnb_number': '3',
            'hardware': 'AirSpeed_2200/AirSpeed_2200',
            'band': 'n48',
            'bw': '40+40MHz',
            'numerology': '1',
            'scs': '30Khz',
            'imsi': 200010001234563
        },
        '2': {
            'gnb_number': '4',
            'hardware': 'AirSpeed_2200/AirSpeed_2200',
            'band': 'n48',
            'bw': '20+40MHz',
            'numerology': '1',
            'scs': '40Khz',
            'imsi': 200010001234564
        }
    },
    {
        '1': {
            'gnb_number': '5',
            'hardware': 'AirSpeed_2200/AirSpeed_2200',
            'band': 'n48',
            'bw': '40+20MHz',
            'numerology': '1',
            'scs': '50Khz',
            'imsi': 200010001234565
        }
    },
    {
        '1': {
            'gnb_number': '5',
            'hardware': 'AirSpeed_2200/AirSpeed_2200',
            'band': 'n48',
            'bw': '40+20MHz',
            'numerology': '1',
            'scs': '50Khz',
            'imsi': 200010001234565
        },
        '2': {
            'gnb_number': '4',
            'hardware': 'AirSpeed_2200/AirSpeed_2200',
            'band': 'n48',
            'bw': '20+40MHz',
            'numerology': '1',
            'scs': '40Khz',
            'imsi': 200010001234564
        }
    },
    {
        '1': {
            'gnb_number': '2',
            'hardware': 'AirSpeed_2200/AirSpeed_2200',
            'band': 'n48',
            'bw': '20MHz',
            'numerology': '1',
            'scs': '20Khz',
            'imsi': 200010001234562
        },
        '2': {
            'gnb_number': '3',
            'hardware': 'AirSpeed_2200/AirSpeed_2200',
            'band': 'n48',
            'bw': '40+40MHz',
            'numerology': '1',
            'scs': '30Khz',
            'imsi': 200010001234563
        },
    }
]

ues_imsi_list = [200010001234561, 200010001234562, 200010001234563, 200010001234564, 200010001234565]

features_data_dict = {
    'SW Upgrade': {
        'SW Upgrade to new release GA - 1': {
            'Feature Group Name': ['SW Upgrade', 'Sanity Test'],
            'Test Plan Number': 'SVGA-1',
            'SIR Number': 'SVGA-100',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'SW Upgrade succeeded',
                    'actual_results': 'SW Upgrade succeeded but Unexpected Event Observed: Software Activate'
                }
            }
        },
        'SW Upgrade to new release GA - 2': {
            'Feature Group Name': ['SW Upgrade', 'Sanity Test'],
            'Test Plan Number': 'SVGA-2',
            'SIR Number': 'SVGA-200',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'SW Upgrade succeeded',
                    'actual_results': 'Fail to read cucp version,may-be NR_cli issue'
                }
            }
        },
        'SW Upgrade to new release GA - 3': {
            'Feature Group Name': ['SW Upgrade', 'Sanity Test'],
            'Test Plan Number': 'SVGA-3',
            'SIR Number': 'SVGA-300',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'SW Upgrade succeeded',
                    'actual_results': 'Fail to read cucp version,may-be NR_cli issue'
                }
            }
        },
    },

    'Throughput Performance Long Run': {
        'Throughput PTP 1h': {
            'Feature Group Name': ['Throughput Test', 'Sanity Test'],
            'Test Plan Number': 'SVGA-4',
            'SIR Number': 'SVGA-400',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'Pods Restart Counter should be 1',
                    'actual_results': 'Pods Restart Counters: RU: 1, CUCP: 1, CUUP: 1, DU: 1'
                }
            }
        },
        'Throughput PT2P 1h': {
            'Feature Group Name': ['Throughput Test', 'Sanity Test'],
            'Test Plan Number': 'SVGA-5',
            'SIR Number': 'SVGA-500',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'Pods Restart Counter should be 2',
                    'actual_results': 'Pods Restart Counters: RU: 2, CUCP: 2, CUUP: 2, DU: 2'
                }
            }
        },
        'Throughput PTP 24h': {
            'Feature Group Name': ['Throughput Test', 'Sanity Test'],
            'Test Plan Number': 'SVGA-6',
            'SIR Number': 'SVGA-600',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'Pods Restart Counter should be 3',
                    'actual_results': 'Pods Restart Counters: RU: 3, CUCP: 3, CUUP: 3, DU: 3'
                }
            }
        },
        'Throughput PT2P 24h': {
            'Feature Group Name': ['Throughput Test', 'Sanity Test'],
            'Test Plan Number': 'SVGA-7',
            'SIR Number': 'SVGA-700',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'Pods Restart Counter should be 4',
                    'actual_results': 'Pods Restart Counters: RU: 4, CUCP: 4, CUUP: 4, DU: 4'
                }
            }
        },
    },

    'Throughput Performance Short Run': {
        'Throughput PTP 1h': {
            'Feature Group Name': ['Throughput Test', 'Sanity Test'],
            'Test Plan Number': 'SVGA-5',
            'SIR Number': 'SVGA-500',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'Pods Restart Counter should be 1',
                    'actual_results': 'Pods Restart Counters: RU: 1, CUCP: 1, CUUP: 1, DU: 1'
                }
            }
        },
        'Throughput PT2P 1h': {
            'Feature Group Name': ['Throughput Test', 'Sanity Test'],
            'Test Plan Number': 'SVGA-6',
            'SIR Number': 'SVGA-600',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'Pods Restart Counter should be 2',
                    'actual_results': 'Pods Restart Counters: RU: 2, CUCP: 2, CUUP: 2, DU: 2'
                }
            }
        },
        'Throughput PTP 24h': {
            'Feature Group Name': ['Throughput Test', 'Sanity Test'],
            'Test Plan Number': 'SVGA-7',
            'SIR Number': 'SVGA-700',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'Pods Restart Counter should be 3',
                    'actual_results': 'Pods Restart Counters: RU: 3, CUCP: 3, CUUP: 3, DU: 3'
                }
            }
        },
        'Throughput PT2P 24h': {
            'Feature Group Name': ['Throughput Test', 'Sanity Test'],
            'Test Plan Number': 'SVGA-8',
            'SIR Number': 'SVGA-800',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'Pods Restart Counter should be 4',
                    'actual_results': 'Pods Restart Counters: RU: 4, CUCP: 4, CUUP: 4, DU: 4'
                }
            }
        },
    },

    'Full PNP': {
        'Full_PNP_Flow': {
            'Feature Group Name': ['PNP Test', 'Sanity Test'],
            'Test Plan Number': 'SVGA-9',
            'SIR Number': 'SVGA-900',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'Expected Events Observed',
                    'actual_results': 'Expected Events not Observed'
                }
            }
        },
        'gNB_Winet_PNP_Flow': {
            'Feature Group Name': ['PNP Test', 'Sanity Test'],
            'Test Plan Number': 'SVGA-11',
            'SIR Number': 'SVGA-110',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'Resthub Events Validation should Pass',
                    'actual_results': 'Winet PnP passed Unexpected Resthub Event Observed: SAS Server HTTP Error Change'
                }
            }
        },
    },

    'Robustness functionality': {
        'gNB_Power_Cycle_GPS_Lock_Unlock_Holdover_Loop_5': {
            'Feature Group Name': ['Robustness Test', 'Sanity Test'],
            'Test Plan Number': 'SVGA-12',
            'SIR Number': 'SVGA-120',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'Expected Events Observed',
                    'actual_results': 'Expected Events not Observed'
                }
            }
        },
        'IODT 2': {
            'Feature Group Name': ['Robustness Test', 'Sanity Test'],
            'Test Plan Number': 'SVGA-13',
            'SIR Number': 'SVGA-130',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'Expected Events Observed',
                    'actual_results': 'Expected Events not Observed'
                }
            }
        },
        'IODT 3': {
            'Feature Group Name': ['Robustness Test', 'Sanity Test'],
            'Test Plan Number': 'SVGA-14',
            'SIR Number': 'SVGA-140',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'Expected Events Observed',
                    'actual_results': 'Expected Events not Observed'
                }
            }
        },
        'IODT 4': {
            'Feature Group Name': ['Robustness Test', 'Sanity Test'],
            'Test Plan Number': 'SVGA-15',
            'SIR Number': 'SVGA-150',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'SSH::XPU Running on Board',
                    'actual_results': 'SSH::XPU not in Running State'
                }
            }
        },
        'IODT 5': {
            'Feature Group Name': ['Robustness Test', 'Sanity Test'],
            'Test Plan Number': 'SVGA-16',
            'SIR Number': 'SVGA-160',
            'Status': {
                'PASS': {
                    'expected_results': '',
                    'actual_results': 'PASS'
                },
                'FAIL': {
                    'expected_results': 'Expected Events Observed',
                    'actual_results': 'Expected Events not Observed'
                }
            }
        },
    },

    # 'Nessus': {
    #     'Test 1': {
    #         'Feature Group Name': ['Nessus Test', 'Sanity Test'],
    #         'Test Plan Number': 'SVGA-17',
    #         'SIR Number': 'SVGA-170',
    #         'Status': {
    #             'PASS': {
    #                 'expected_results': '',
    #                 'actual_results': 'PASS'
    #             },
    #             'FAIL': {
    #                 'expected_results': 'No new vulnerability',
    #                 'actual_results': 'number new vulnerability was found'
    #             },
    #         }
    #     },
    # },
}

warning_list = [
    'warning 1',
    'warning 2',
    'warning 2',
    'warning 2',
    'warning 5',
]

error_list = [
    'error 1',
    'error 2',
    'error 3',
    'error 3',
    'error 5',
]
