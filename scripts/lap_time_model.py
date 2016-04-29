# import general libraries
import pandas as pd
import numpy as np
import datetime
import os
import cPickle as pickle
import scripts.f1_scripts  as f1
# import ML libraries
import statsmodels.api as sms
from sklearn.linear_model import LinearRegression
from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import AdaBoostRegressor
# import plotting libraries
import matplotlib.pyplot as plt
import seaborn as sn

# Load driver list as GLOBAL variable
DRIVER_LIST = pd.read_csv('data/drivers.csv')

def assign_color(tire):
    colors = {'Ultra': 'm', 'Super': 'r', 'Soft': 'y',
                'Medium': 'w', 'Hard': 'k', 'Intermediate': 'g'}
    return colors[tire]

def assign_ordinal(tire):
    vals = {'Ultra': 1, 'Super': 2, 'Soft': 3, 'Medium': 4,
                'Hard': 5, 'Intermediate': 6}
    return vals[tire]



if __name__ == '__main__':
    # Create a list of the available races to date that we can use for training
    races = os.listdir('data/fia')
    races = races[1:]

    # Create DataFrame of all laps for all drivers in all races
    list_of_times = []
    for race in races:
        lap_times = create_race_features(race)
        list_of_times.append(lap_times)
        print '{} complete.'.format(race)
    all_lap_times = pd.concat(list_of_times)
    all_lap_times['YEAR'] = all_lap_times['YEAR'].astype(int)
    all_lap_times.reset_index(inplace=True, drop=True)

    # Add column to classify laps race under Safety Car
    all_lap_times['SAFETY'] = all_lap_times.apply(
            lambda x: f1.assign_safety(x['TRACK'], x['YEAR'], x['LAP']), axis=1)

    # Add Stints column to count laps since last tire change
    all_lap_times = f1.assign_stint_lap(all_lap_times)

    # Remove pit laps and out laps, remove safety laps, remove starting lap
    no_pits = remove_pits(all_lap_times)
    no_pits.drop(no_pits[no_pits['LAP'] == 1].index, axis=0, inplace=True)
    no_safety = no_pits[no_pits['SAFETY'] == 0]

    # Load Track Data
    track_data = f1.load_data(features=False)
    tracks.drop(['T_TEMP_MIN'], axis=1, inplace=True)

    # Create full feature dataframe
    lap_features = pd.merge(no_safety, tracks, how='left', on=['TRACK', 'YEAR'])
    regression_features = lap_features.drop(['NO', 'GAP', 'TRACK', 'YEAR', 'RACE', 'SAFETY'], axis=1)
    regression_dummies = pd.get_dummies(all_regression_features, columns=['TIRE'])
    regression_dummies.drop('TIRE_Intermediate', axis=1, inplace=True)

    # Create feature matrix, targets, train_test_split
    y = regression_dummies.pop('TIME')
    X = regression_dummies
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    # Linear Regression Model
    model = sms.OLS(y_train, sms.add_constant(X_train)).fit()
    summary = model.summary()
    print summary

    # Random Forest Regressor
    rfr = RandomForestRegressor(n_estimators=20, max_features='sqrt', oob_score=True)
    rfr.fit(X2_train, y2_train)
    rfr2.oob_score_
    rfr2.score(X2_train, y2_train)
    print 'Test Score: ', rfr2.score(X2_test, y2_test)

    with open('model.pickle', 'wb') as f:
        pickle.dump(model, f)
