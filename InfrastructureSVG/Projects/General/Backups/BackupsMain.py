import yaml
import time


def my_import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def get_backup_class():
    with open('backup_class.yml', "r") as f:
        try:
            return yaml.safe_load(f)['class']
            # print(f'{backup_class_list}')
        except yaml.YAMLError as err:
            print(f'{err}')


def print_title(while_index, index, backup_class):
    print('\n\n')
    title = f'### cycle: {while_index}.{index}, class: {backup_class.split(".")[-1]} ###'
    print(f'\n{"#" * len(title)}')
    print(f'{title}\n{"#" * len(title)}')


def send_mail():
    print('send a mail')


def backup_main():
    while_index = 0
    while True:
        while_index += 1

        backup_class_list = get_backup_class()
        if backup_class_list:
            for index, backup_class in enumerate(backup_class_list, start=1):
                print_title(while_index, index, backup_class)
                try:
                    app_class = my_import(backup_class)
                    app_obj = app_class()
                    app_obj.process()
                except Exception as err:
                    print(err)
                time.sleep(1)
        else:
            send_mail()


if __name__ == '__main__':
    backup_main()
