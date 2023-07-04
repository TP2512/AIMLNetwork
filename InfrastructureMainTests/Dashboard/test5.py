import pandas as pd
import numpy as np
import re
from pandas.io.formats.style import Styler
from IPython.display import HTML

df = pd.DataFrame([[38.0, 2.0, 18.0, 22.0, 21, np.nan], [19, 439, 6, 452, 226, 232]],
                  index=pd.Index(['Tumour (Positive)', 'Non-Tumour (Negative)'], name='Actual Label:'),
                  columns=pd.MultiIndex.from_product([['Decision Tree', 'Regression', 'Random'], ['Tumour', 'Non-Tumour']],
                                                     names=['Model:', 'Predicted:']))

props = 'font-family: "Times New Roman", Times, serif; color: #e83e8c; font-size:1.3em;'
html = Styler(df, uuid_len=0, cell_ids=False).set_table_styles(
    [
        {'selector': 'td', 'props': props},
        {'selector': '.col1', 'props': 'color:green;'},
        {'selector': '.level0', 'props': 'color:blue;'}
    ]
).render(). \
    replace('blank', ''). \
    replace('data', ''). \
    replace('level0', 'l0'). \
    replace('col_heading', ''). \
    replace('row_heading', '')

html = re.sub(r'col[0-9]+', lambda x: x.group().replace('col', 'c'), html)
print()

with open('html_file.html', 'w') as f:
    f.write(html)

print()
