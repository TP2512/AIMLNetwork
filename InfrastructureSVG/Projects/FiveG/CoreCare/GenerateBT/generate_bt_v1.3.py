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


if __name__ == '__main__':
    c = True
    while c:
        try:
            back_trace_file_path = f'{input("please enter the full path of the core file (tar.gz): ")}'
            if not os.path.exists(back_trace_file_path):
                print(f'\nError, not found path: {back_trace_file_path}')
            else:
                tar = tarfile.open(back_trace_file_path, encoding='utf-8')

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
                    print('\nError, back trace was not generated')
                else:
                    back_trace = build_back_trace(back_trace_list)
                    if back_trace == '':
                        print('\nError, back trace was not created')
                    else:
                        print('\nThe back trace is:')
                        for part_bt in back_trace.split(f' -> '):
                            print(part_bt)

                        print(f'\n\nThe back trace in 1 line is: \n{back_trace}\n\n')
        except EOFError as err:
            common_exception(err)
            print(
                f'\n##########################################\n'
                f'# please check if the file is not empty! #'
                f'\n##########################################\n'
            )
        except Exception as err:
            common_exception(err)
        finally:
            c = input("\npress enter to exit (closing the cmd) or C to continue to another BT: ")
            if c.upper() == 'C':
                c = True
            else:
                c = False

            if c:
                clear_screen = input('\npress "Y" to clear the screen, press "N" to not clear the screen: ')
                if clear_screen.upper() == 'Y':
                    os.system('cls')
                else:
                    pass
