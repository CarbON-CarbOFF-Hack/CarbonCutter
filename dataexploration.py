import pandas as pd

hourly_energy = pd.read_csv('data/hourly_energy.csv')

print(hourly_energy.shape)
print(hourly_energy.columns)
print(hourly_energy.iloc[0])