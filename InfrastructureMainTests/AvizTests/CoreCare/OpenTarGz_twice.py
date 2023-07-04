import tarfile
import yaml


def read_tar_gz_file(tar, get_members, tr_gz_file_name: str):
    fp_read = None
    for tr_gz_name in get_members:
        if tr_gz_file_name in tr_gz_name.name:
            fp = tar.extractfile(tr_gz_name)
            fp_read = fp.read()
            break
    return fp_read


def get_tar_gz_file(back_trace_file_path: str):
    tar = tarfile.open(back_trace_file_path, encoding='utf-8')
    get_members = tar.getmembers()
    return tar, get_members


if __name__ == '__main__':
    # path_ = f'C:\\Users\\azaguri\\Desktop\\CORE_data.tar.gz'
    path_ = f'C:\\Users\\azaguri\\Desktop\\CORE_data_gnb_du_19.00-84-0.0_2021_09_22_12_43_28.tar.gz'
    # path_ = f'C:\\Users\\azaguri\\Desktop\\\CORE_data\\CORE_data.tar'
    tar_1, get_members_1 = get_tar_gz_file(path_)
    fp_read_ = read_tar_gz_file(tar_1, get_members_1, 'du_systeminfo')
    fp_read__ = fp_read_.decode('UTF-8').replace(":", ": ").replace("\n\n", "\n")
    du_systeminfo = yaml.safe_load(fp_read__)
    print(du_systeminfo)

    print()
