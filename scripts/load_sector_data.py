import pandas as pd
import numpy as np


def get_sector_times(df):
    rows = df.shape[0] / 3
    sector1, others = df.iloc[:22, :], df.iloc[22:, :]
    sector2, sector3 = others.iloc[:rows, :], others.iloc[rows:, :]
    all_sectors = pd.merge(sector2, sector3, on=[0, 1])
    all_sectors = pd.merge(sector1, all_sectors, on=[0,1])
    all_sectors.columns = ['NO', 'DRIVER', 'SECTOR_1', 'SECTOR_2', 'SECTOR_3']
    all_sectors.drop(0, inplace=True)
    all_sectors[['SECTOR_1', 'SECTOR_2', 'SECTOR_3']] = all_sectors[['SECTOR_1', 'SECTOR_2', 'SECTOR_3']].astype(float)
    return all_sectors

if __name__ == '__main__':
    df = pd.read_csv('data/2016_1_austrailia/tabula-2016_1_race_best_sector_times.csv', header=None)
