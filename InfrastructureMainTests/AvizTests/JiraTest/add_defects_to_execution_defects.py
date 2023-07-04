import requests
import json


def get_test_exec_id(test_exec_key: str) -> tuple[int, int]:
    url = f'https://TestspanAuto:air_auto1@helpdesk.airspan.com/rest/raven/1.0/testruns?testExecKey={test_exec_key}'
    response_data = requests.get(url=url, timeout=600)
    return response_data.status_code, json.loads(response_data.text)[0]['id']


def add_defects_to_execution_defects(test_exec_key: str, defects: list) -> bool:
    status_code, test_exec_id = get_test_exec_id(test_exec_key)
    if status_code == 200:
        body = defects
        url = f'https://TestspanAuto:air_auto1@helpdesk.airspan.com/rest/raven/1.0/testrun/{test_exec_id}/defects'
        response_data = requests.post(url=url, json=body, timeout=240)
        if response_data.status_code == 200:
            return True
    return False


if __name__ == '__main__':
    t_f = add_defects_to_execution_defects(test_exec_key='SVGA-7304', defects=['DEF-41449', 'DEF-41450', 'DEF-41894'])
    print(t_f)

    print()
