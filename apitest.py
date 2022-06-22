import pandas as pd

electric_map = pd.read_csv('data/electric_map.csv')

print(electric_map.shape)
print(electric_map.columns)
print(electric_map.iloc[0])