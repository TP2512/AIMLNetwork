

if __name__ == '__main__':
    path = 'C:\\Users\\Administrator\\Desktop\\DU-1\\core'
    file_name = 'du_core_info_2022-01-30.08_40_02.txt'
    with open(f'{path}\\{file_name}', 'r') as f:
        bt = f.read()
    print(bt)
    print(bt.split('\n'))

    print()
