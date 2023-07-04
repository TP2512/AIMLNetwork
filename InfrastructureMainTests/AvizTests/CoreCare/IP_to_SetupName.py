import pandas as pd


if __name__ == '__main__':
    print('\\\\172.25.0.4\\data\\SVG\\SVG LAB\\LAB Management\\IP_table_SVG_LAB.xls')
    columns = ['IP address', 'IPv6 Address', 'Equ. Name', 'Cabinet Location name', 'Equipment Type', 'Hostname']
    ip_table_svg_lab = pd.read_excel('\\\\172.25.0.4\\data\\SVG\\SVG LAB\\LAB Management\\IP_table_SVG_LAB.xls', sheet_name='IP_Table_172.20.60.x', header=1)
    entity_name = ip_table_svg_lab.loc[ip_table_svg_lab['IP address'] == '172.20.62.192']
    print(entity_name['Equ. Name'].values[0])

    print()
