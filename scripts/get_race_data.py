import pandas as pd
import numpy as np
import datetime
import os
from f1_scripts import (assign_lap,
                        get_tires,
                        get_sector_times,
                        convert_time,
                        get_avg_lap)

# Load driver list as GLOBAL variable
DRIVER_LIST = pd.read_csv('data/drivers.csv')

def create_race_features(filename):
    year, race_num, track = filename.split('_')
    # Load lap times for all drivers
    lap_data = pd.read_csv('data/lap_history/{filename}_lap_history.csv'.format(filename=filename), header=None)
    lap_times = assign_lap(lap_data)
    lap_times['TIME'] = convert_time(lap_times['TIME'])
    lap_times.sort_values(by=['NO', 'LAP'], inplace=True)

    # Load Tire strategy data
    tire_data = pd.read_csv('data/tire_strategy/{filename}.csv'.format(filename=filename))
    tire_strat = get_tires(tire_data)

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
    print all_lap_times.shape

    # # Load Track Data
    # tracks = pd.read_csv('data/track_profiles - Sheet1.csv')
    # tracks.drop('LAPS', axis=1, inplace=True)
    #
    # # Create full feature dataframe
    # lap_features.merge(tracks, how='left', on=['TRACK', 'YEAR'])
