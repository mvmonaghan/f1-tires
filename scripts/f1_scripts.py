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

def load_tracks(features=True):
    if features:
        tracks = pd.read_csv('data/track_features.csv')
    else:
        tracks = pd.read_csv('data/track_history.csv')
    tracks.drop('LAPS', axis=1, inplace=True)
    tracks['TRACK'] = tracks['TRACK'].apply(lambda x: x.lower())
    return tracks

def load_drivers():
    # Load driver list as GLOBAL variable
    return pd.read_csv('data/drivers.csv')

def create_race_features(filename):
    year, race_num, track = filename.split('_')
    # Load lap times for all drivers
    lap_data = pd.read_csv('data/lap_history/{filename}_lap_history.csv'.format(filename=filename), header=None)
    lap_times = assign_lap(lap_data)
    lap_times['TIME'] = convert_time(lap_times['TIME'])
    lap_times.sort_values(by=['NO', 'LAP'], inplace=True)
    lap_times['LAP'] = lap_times['LAP'].astype(int)
    # Load Tire strategy data
    tire_data = pd.read_csv('data/tire_strategy/{filename}.csv'.format(filename=filename))
    tire_strat = get_tires(tire_data)
    # Load Driver list
    driver_list = load_drivers()
    # Join Driver, Name, No. to tire data and sort by No.
    tire_strat = pd.merge(driver_list, tire_strat, on='NAME')
    tire_strat.drop(['NAME', 'DRIVER'], axis=1, inplace=True)
    # Append tire data to lap data
    mask = tire_strat.iloc[:,1:].notnull().values
    lap_times['TIRE'] = tire_strat[tire_strat.columns[1:]].values[mask].flatten()
    lap_times['TRACK'] = track
    lap_times['YEAR'] = int(year)
    lap_times['RACE'] = race_num
    lap_times['GAP'] = lap_times['GAP'].apply(lambda x: x.strip())
    return lap_times

def assign_stint_lap(df):
    df['STINT_LAP'] = 1
    idx = df[df['GAP'] == 'PIT'].index
    start = 0
    for val in idx:
        df['STINT_LAP'].ix[start:val] = df.ix[start:val]['STINT_LAP'].cumsum()
        start = val + 1
    end = df.index[-1]
    df['STINT_LAP'].ix[start:end] = df.ix[start:end]['STINT_LAP'].cumsum()
    return df

def remove_pits(df):
    idx = []
    previous = None
    for row in df.iterrows():
        if row[1]['GAP'] == 'PIT' or previous == 'PIT':
            idx.append(row[0])
        previous = row[1]['GAP']
    return df.drop(idx, axis=0)

def plot_drivers(df, race):
    sn.set_style(style='whitegrid')
    year, race_num, track = race.split('_')
    this_race = df[(df['TRACK'] == track) & (df['YEAR'] == int(year))]
    for num in this_race['NO'].unique():
        driver_idx = this_race['NO'] == num
        plt.figure(figsize=(12,6))
        plt.title('{} {} - Driver No. {}'.format(track.upper(), year, num))
        plt.xlim([0, this_race['LAP'].max() + 1])
        plt.scatter(this_race['LAP'][driver_idx], this_race['TIME'][driver_idx], c=this_race['TIRE'][driver_idx].apply(assign_color), alpha=1)
    plt.show()

def plot_race(df, race):
    year, race_num, track = race.split('_')
    this_race = df[(df['TRACK'] == track) & (df['YEAR'] == int(year))]
    plt.figure(figsize=(12,6))
    plt.title('{} {}'.format(track.upper(), year))
    plt.xlim([0, this_race['LAP'].max() + 1])
    plt.scatter(this_race['LAP'], this_race['TIME'], c=this_race['TIRE'].apply(assign_color), alpha=.5)
    plt.show()
