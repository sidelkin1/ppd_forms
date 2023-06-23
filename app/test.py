from typing import Optional


def fun(a, b: Optional[int]):
    pass


print(dir(fun))
print(fun.__annotations__)

# class_variables = [attribute for attribute in dir(X)
#                    if not attribute.startswith('__')
#                    and not callable(getattr(X, attribute))
#                    ]

# print(class_variables)

# import pandas as pd

# path = r'D:\Dev\ppd_forms\data\results.csv'
# df = pd.read_csv(path, encoding='utf8')

# df.insert(6, 'cid_layer', None)
# df[['cid_layer', 'layer']] = df['layer'].str.split(': ', expand=True)
# df['cid_layer'] = df['cid_layer'].str.replace(':', '')

# df.to_csv('results.csv', index=False)
