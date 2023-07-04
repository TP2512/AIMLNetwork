import pandas as pd
import numpy as np
import re
from pandas.io.formats.style import Styler
from IPython.display import HTML


def style_negative(v, props=''):
    return props if v < 0 else None


def highlight_max(s, props=''):
    return np.where(s == np.nanmax(s.values), props, '')


np.random.seed(0)
df2 = pd.DataFrame(np.random.randn(10,4), columns=['A','B','C','D'])
# print(df2.style)
s2 = df2.style.applymap(style_negative, props='color:red;')\
              .applymap(lambda v: 'opacity: 20%;' if (v < 0.3) and (v > -0.3) else None)
# print(s2)
s2.apply(highlight_max, props='background-color: #00875a; border-color: #00875a; color: #fff; border: 0 solid #42526e; border-radius: 3px; color: #fff; display: inline-block; font-size: 11px; font-weight: 700; line-height: 1; margin: 0; padding: 2px 5px 3px; text-align: center; text-decoration: none; text-transform: uppercase;', axis=0)

s2.apply(highlight_max, props='color:white;background-color:pink;', axis=1)\
  .apply(highlight_max, props='color: rgb(255,255,255)', axis=None)

print(s2.to_html())
print()
