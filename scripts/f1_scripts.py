import pandas as pd
import numpy as np
import datetime
import os

def assign_lap(df):
    df['LAP'] = 1
    cols = ['NO', 'GAP', 'TIME', 'LAP']
    drivers = df[0].unique()
    data = df.values
    for driver in drivers:
        data[data[:,0] == driver, 3] = data[data[:,0] == driver, 3].cumsum()
    return pd.DataFrame(data=data, columns=cols)

def convert_time(arr):
    arr = arr.apply(lambda x: x.strip())
    arr = arr.apply(lambda x: datetime.datetime.strptime(x,'%M:%S.%f'))
    timedelta = arr - datetime.datetime.strptime('00:00.0','%M:%S.%f')
    secs = timedelta.apply(lambda x: x / np.timedelta64(1, 's'))
    return secs

def get_tires(df):
    arr = df.values
    all_strategies = []
    for row in arr:
        strategy = [row[0]]
        for item in row[1:]:
            try:
                tire, laps = item.split()
                laps = int(laps.replace('(', '').replace(')', ''))
                stint = []
                for i in xrange(laps):
                    stint.append(tire)
                strategy.extend(stint)
            except:
                pass
        all_strategies.append(strategy)
    df = pd.DataFrame(data=all_strategies)
    column_names = ['NAME']
    column_names.extend([i for i in xrange(1, df.shape[1])])
    df.columns = column_names
    return df

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

def get_avg_lap(df):
    grouped = lap_times.drop(['GAP', 'LAP', 'RACE'], axis=1).groupby(['NO', 'TIRE', 'TRACK', 'YEAR'], as_index=False)
    avg_laps = pd.merge(grouped.count(), grouped.mean(), how='left', on=['NO', 'TIRE', 'TRACK', 'YEAR'])
    avg_laps.columns = ['NO', 'TIRE', 'TRACK', 'YEAR', 'COUNT', 'TIME']
    return avg_laps
