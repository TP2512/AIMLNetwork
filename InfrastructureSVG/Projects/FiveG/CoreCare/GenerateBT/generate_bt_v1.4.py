import os
import sys
import tarfile


def common_exception(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    # print(exc_type, fname, exc_tb.tb_lineno)
    print('The Exception is: ')
    print(e)
    print('The error in: ')
    print('File: ' + str(fname))
    print('Class: ' + str(exc_type))
    print('Line: ' + str(exc_tb.tb_lineno))


def print_introduction():
    print('##########################################')
    print('### CocreCare Generate Back Trace v1.4 ###')
    print('##########################################')
    print('\n\n')


def build_back_trace(bt_list):
    """ Build "Back Trace" from core file """

    bt = ''

    flag = False
    list_ignore = ['/usr/']
    for row in bt_list:
        # if '/usr/' in row[0] or '' == row[0]:
        if any([True if i in row else False for i in list_ignore]) or row == '':
            if flag:
                continue
            else:
                flag = True
                bt = ''
        elif 'WORKER_THREAD' in row.upper() or 'THREAD_START' in row.upper():
            break
        else:
            bt += f' -> {row}'

    return bt[4:]


def back_trace_process(back_trace_file_path_):
    tar = tarfile.open(back_trace_file_path_, encoding='utf-8')

    back_trace_list = None
    tr_gz_name = None
    for tr_gz_name in tar.getmembers():
        if 'core_info' in tr_gz_name.name:
            fp = tar.extractfile(tr_gz_name)
            fp_read = fp.read()
            back_trace_list = fp_read.decode("UTF-8").split("\n")
            break
    tar.close()

    if not back_trace_list or not tr_gz_name:
        return '\nError, back trace was not generated'
    else:
        back_trace = build_back_trace(back_trace_list)
        if back_trace == '':
            return '\nError, back trace was not created'
        else:
            return f'The back trace is: \n{back_trace}\n\n'


def save_bt_to_file(bt_file_path, bt_):
    bt_ = bt_.replace(f' -> ', '\n')
    with open(bt_file_path.replace('.tar.gz', '.txt'), 'w') as file_:
        file_.write(bt_)
        file_.close()


if __name__ == '__main__':
    print_introduction()

    c = True
    while c:
        try:
            text_ = 'please enter specific path to core file (tar.gz) or path to the folder with Cores file: '
            back_trace_path = f'{input(text_)}'

            if not os.path.exists(back_trace_path):
                print(f'\nError, path not found: {back_trace_path}')
                continue
            else:  # file path
                if '.tar.gz' in back_trace_path:
                    back_trace_file_path = back_trace_path
                    back_trace_ = back_trace_process(back_trace_file_path)
                    for part_bt in back_trace_.split(f' -> '):
                        print(part_bt)
                    print(f'\n\n{back_trace_.replace("The back trace is:", "The back trace in one line is:")}\n\n')
                    save_bt_to_file(back_trace_file_path, back_trace_)
                else:  # folder path
                    for r, d, f in os.walk(back_trace_path):
                        for file in f:
                            if '.tar.gz' in file:
                                back_trace_file_path = f'{r}\\{file}'
                                back_trace_ = back_trace_process(back_trace_file_path)
                                save_bt_to_file(back_trace_file_path, back_trace_)
                        print('\n.txt files were created in the source folder by the Cores names\n')
                        break
        except EOFError as err:
            common_exception(err)
            print(
                f'\n##########################################\n'
                f'# please check if the file is not empty! #'
                f'\n##########################################\n'
            )
        except Exception as err:
            common_exception(err)

        c = input("\npress enter to exit (closing the cmd) or C to continue to another BT: ")
        if c.upper() == 'C':
            c = True
        else:
            c = False

        if c:
            clear_screen = input('\npress "Y" to clear the screen, press "N" to not clear the screen: ')
            if clear_screen.upper() == 'Y':
                os.system('cls')
                print_introduction()
            else:
                pass
