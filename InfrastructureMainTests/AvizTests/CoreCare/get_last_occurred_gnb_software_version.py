def get_last_occurred_gnb_software_version(current_version, last_occurred_gnb_software_version):
    current_sr_version = current_version.split("-", 1)[0]
    current_version = current_version.split("-", 1)[1]

    if float(last_occurred_gnb_software_version.split("-", 1)[0]) == float(current_sr_version):
        if (
                int(current_version.split("-", 1)[0]) > int(last_occurred_gnb_software_version.split("-", 1)[1].split("-", 1)[0])
        ) or \
                (
                        int(current_version.split("-", 1)[0]) == int(last_occurred_gnb_software_version.split("-", 1)[1].split("-", 1)[0]) and
                        float(current_version.split("-", 1)[1]) > float(last_occurred_gnb_software_version.split("-", 1)[1].split("-", 1)[1])
                ):
            print('x')
        else:
            print('z')
    else:
        print('y')


if __name__ == '__main__':
    get_last_occurred_gnb_software_version(current_version='19.00-114-0.1', last_occurred_gnb_software_version='19.00-114-0.0')
    print()
