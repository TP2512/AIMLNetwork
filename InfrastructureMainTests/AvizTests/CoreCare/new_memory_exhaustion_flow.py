import re
import pandas as pd
import os


"""
How to analyze new_memory_exhaustion_flow.txt:
----------------------------------------------

1. Utilization > 90% + lower BucketIndex 

2. BucketIndex -> Bucket (2 first)

3. summary: M.E: Bucket[4], Utilization[x%] -> topAlloc: [SrcFile[func_name]_1:LineNo, SrcFile[func_name]_2:LineNo]
    For example: M.E: Bucket[4], Utilization[95%] -> topAlloc: [cmn_kpi.c:198, ss_msg.c:1079]
"""


def is_number(number):
    try:
        float(number)
        return True
    except ValueError:
        return False
    except Exception:
        return False


def get_dataframe_table(columns, table):
    dataframe = pd.DataFrame(columns=columns)
    for index, line in enumerate(table.split('\n'), start=0):
        if not line or index == 0:
            continue

        new_row = pd.DataFrame([line.replace('%', '').split()], columns=columns)
        dataframe = pd.concat([dataframe, new_row], ignore_index=True)
    return dataframe


def get_lower_bucket_ndex_of_max_utilization(memory_exhaustion):
    ssi_memory_utilization_table = memory_exhaustion.split('SSI Memory Utilization')[1].split('Top 20 allocators of SSI Dynamic Configuration Memory')[0]
    ssi_memory_utilization_table = re.sub(r"( {10,1000}\n-{1,1000})\n", "", ssi_memory_utilization_table)
    ssi_memory_utilization_table = re.sub(r"(-{1,1000})\n", "", ssi_memory_utilization_table)

    columns = ['BucketIndex', 'ReqSize', 'TotalNumOfBlocks', 'AllocCnt', 'Utilization']
    ssi_memory_utilization_dataframe = get_dataframe_table(columns, ssi_memory_utilization_table)
    new_dataframe = pd.DataFrame(columns=columns)
    for i, line in ssi_memory_utilization_dataframe.sort_values(by=['Utilization'], ascending=False).iterrows():
        if is_number(number=line['Utilization'].isdecimal()) and float(line['Utilization']) >= 90 and float(line['Utilization']) >= float(ssi_memory_utilization_dataframe['Utilization'].astype(float).max()):
            new_row = pd.DataFrame([line.tolist()], columns=columns)
            new_dataframe = pd.concat([new_dataframe, new_row], ignore_index=True)

    return new_dataframe['BucketIndex'].min(), new_dataframe['Utilization'].max()


def get_top_20_allocators_of_ssi_table(memory_exhaustion):
    top_20_allocators_of_ssi_table = memory_exhaustion.split('Top 20 allocators of SSI Dynamic Configuration Memory')[1]
    top_20_allocators_of_ssi_table = re.sub(r"( {1,1000}\n={1,1000})\n", "", top_20_allocators_of_ssi_table)
    top_20_allocators_of_ssi_table = re.sub(r"(={1,1000})\n", "", top_20_allocators_of_ssi_table)

    columns = ['S.No#', 'AllocCnt', 'Bucket', 'RegionId', 'ReqSize', 'LineNo', 'SrcFile']
    return get_dataframe_table(columns, top_20_allocators_of_ssi_table)


def main():
    username = os.getlogin()
    path = f'C:\\Users\\{username}\\Documents\\Temporary - can be deleted\\CoreCare\\du_core_mem_info_mem_leak.txt'
    with open(path, 'r') as f:
        memory_exhaustion_ = f.read()

    lower_bucket_ndex_of_max_utilization, max_utilization = get_lower_bucket_ndex_of_max_utilization(memory_exhaustion_)

    top_20_allocators_of_ssi_dataframe = get_top_20_allocators_of_ssi_table(memory_exhaustion_)
    top_20_allocators_of_ssi_dataframe = top_20_allocators_of_ssi_dataframe.loc[top_20_allocators_of_ssi_dataframe['Bucket'] == str(lower_bucket_ndex_of_max_utilization)]
    print(top_20_allocators_of_ssi_dataframe[:2])

    func_list = [f"{line['SrcFile'].split('/')[-1]}:{line['LineNo']}" for index, line in top_20_allocators_of_ssi_dataframe[:2].iterrows()]
    summary = f'M.E: Bucket[{lower_bucket_ndex_of_max_utilization}], Utilization[{max_utilization}%] -> topAlloc: [{", ".join(func_list)}]'
    print(summary)
    print()


if __name__ == '__main__':
    main()
