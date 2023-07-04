import yaml

if __name__ == '__main__':
    path = 'C:\\Users\\Administrator\\Desktop\\DU-1\\core'
    file_name = 'du_systeminfo_2022-01-30.08_40_05.yaml'
    try:
        with open(f'{path}\\{file_name}', 'r') as stream:
            yaml_data = yaml.safe_load(stream)
        print(yaml_data)
    except Exception as err:
        print(err)
    print()

    from InfrastructureSVG.DateAndTimeFormats.CalculateTime_Infrastructure import CalculateTime
    x = CalculateTime(h=yaml_data['System Running Time']['Hours'], m=yaml_data['System Running Time']['Minutes'], s=yaml_data['System Running Time']['Seconds']).calculate_minutes()
    print(x)

    print()
