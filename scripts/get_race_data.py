import pandas as pd
import numpy as np
import datetime
import os
import f1_scripts as f1

# Load driver list as GLOBAL variable
DRIVER_LIST = pd.read_csv('data/drivers.csv')

def create_race_features(filename):
    year, race_num, track = filename.split('_')
    # Load lap times for all drivers
    lap_data = pd.read_csv('data/lap_history/{filename}_lap_history.csv'.format(filename=filename), header=None)
    lap_times = f1.assign_lap(lap_data)
    lap_times['TIME'] = f1.convert_time(lap_times['TIME'])
    lap_times.sort_values(by=['NO', 'LAP'], inplace=True)

    # Load Tire strategy data
    tire_data = pd.read_csv('data/tire_strategy/{filename}.csv'.format(filename=filename))
    tire_strat = f1.get_tires(tire_data)

    # Join Driver, Name, No. to tire data and sort by No.
    tire_strat = pd.merge(DRIVER_LIST, tire_strat, on='NAME')
    tire_strat.drop(['NAME', 'DRIVER'], axis=1, inplace=True)

    # Append tire data to lap data
    mask = tire_strat.iloc[:,1:].notnull().values
    lap_times['TIRE'] = tire_strat[tire_strat.columns[1:]].values[mask].flatten()
    lap_times['TRACK'] = track
    lap_times['YEAR'] = year
    lap_times['RACE'] = race_num

    return lap_times



if __name__ == '__main__':
    # Create a list of the available races to date that we can use for training
    races = os.listdir('data/fia')
    races = races[1:]
    # Remove bahrain 2015 until data is fixed
    races.pop(13)


    # Create DataFrame of all laps for all drivers in all races
    list_of_times = []
    for race in races:
        lap_times = create_race_features(race)
        list_of_times.append(lap_times)
        print '{} complete.'.format(race)
    all_lap_times = pd.concat(list_of_times)
    all_lap_times['YEAR'] = all_lap_times['YEAR'].astype(int)


    # Load Track Data
    track_data = pd.read_csv('data/track_profiles.csv')
    tracks = track_data.drop('LAPS', axis=1)
    tracks['TRACK'] = tracks['TRACK'].apply(lambda x: x.lower())

    # aggregate lap time by race, driver, and tire type to calculate average times
    grouped = all_lap_times.drop(['GAP', 'LAP', 'RACE'], axis=1).groupby(['NO', 'TIRE', 'TRACK', 'YEAR'], as_index=False)
    avg_laps = pd.merge(grouped.count(), grouped.mean(), how='left', on=['NO', 'TIRE', 'TRACK', 'YEAR'])
    avg_laps.columns = ['NO', 'TIRE', 'TRACK', 'YEAR', 'COUNT', 'TIME_AVG']


    # Create full feature dataframe
    lap_features.merge(tracks, how='left', on=['TRACK', 'YEAR'])
