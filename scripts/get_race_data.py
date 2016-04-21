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

def get_strategies(df):
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
    merged = pd.merge(driver_list, df, on='NAME')
    return merged.drop(['NAME', 'DRIVER'], axis=1)


if __name__ == '__main__':
    # Load driver list for particular season
    driver_list = pd.read_csv('data/2016_drivers.csv')

    # Load lap times for all drivers
    df = pd.read_csv('data/2016_1_austrailia/history_test.csv', header=None)
    df = assign_lap(df)
    df.sort_values(by=['NO', 'LAP'], inplace=True)

    # Convert lap time to seconds
    df['TIME'] = df['TIME'].apply(lambda x: x.strip())
    df['TIME'] = df['TIME'].apply(lambda x: datetime.datetime.strptime(x,'%M:%S.%f'))
    df['timedelta'] = df.TIME - datetime.datetime.strptime('00:00.0','%M:%S.%f')
    df['secs'] = df['timedelta'].apply(lambda x: x / np.timedelta64(1, 's'))

    # Load Tire strategy data
    tire_data = pd.read_csv('data/2016_1_austrailia/2016_1_tires.csv')
    tire_strat = get_strategies(tire_data)
