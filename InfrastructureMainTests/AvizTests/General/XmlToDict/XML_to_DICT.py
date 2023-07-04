import xmltodict
import json


if __name__ == '__main__':
    xml_path = 'test.xml'
    xml_data = open(xml_path, 'r').read()

    dict_data = dict(xmltodict.parse(xml_data, xml_attribs=False))
    print(json.dumps(dict_data, indent=4, sort_keys=True))

    print()


