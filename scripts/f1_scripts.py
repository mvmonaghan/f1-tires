import pandas as pd
import numpy as np
import datetime
import os
from collections import defaultdict

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

def assign_safety(track, year, lap):
    safety_car = {'australia': {2015: {1,2,3},
                                2016: {17}},
                  'china': {2015: {54,55,56},
                            2016: {4,5,6,7,8}},
                  'hungary': {2015: {43,44,45,46,47,48}},
                  'belgium': {2015: {20,21}},
                  'singapore': {2015: {13,14,15,16,17,18,37,38,39,40}},
                  'russia': {2015: {1,2,3,12,13,14,15,16}},
                  'usa': {2015: {5,6,7,27,28,29,30,31,32,37,38,39,43,44,45,46}},
                  'mexico': {2015: {52,53,54,55,56,57}},
                  'malaysia': {2015: {4,5,6}},
                  'monaco': {2015: {63,64,65,66,67,68,69,70}},
                  'austria': {2015: {1,2,3,4,5,6}},
                  'britain': {2015: {1,2,3,33,34}},
                  }
    if track in safety_car:
        if lap in safety_car[track][year]:
            return 1
        else:
            return 0
    else:
        return 0

def get_stints(df):
    previous = None
    laps = []
    times = []
    tires = []
    stint = defaultdict(list)
    for row in df.iterrows():
        if row[1]['GAP'] == 'PIT':
            stint[row[1]['NO']].append((laps, times, tire))
            laps = []
            times = []
            tires = []
        elif previous == 'PIT':
            pass
        else:
            laps.append(row[1]['LAP'])
            times.append(row[1]['TIME'])
            tire.append(row[1]['TIRE'])
        previous = row[1]['GAP']
    return stint

def plot_stints(stint):
    pass
