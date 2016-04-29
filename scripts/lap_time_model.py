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
# # import plotting libraries
# import matplotlib.pyplot as plt
# import seaborn as sn


def assign_color(tire):
    colors = {'Ultra': 'm', 'Super': 'r', 'Soft': 'y',
                'Medium': 'w', 'Hard': 'k', 'Intermediate': 'g'}
    return colors[tire]

def assign_ordinal(tire):
    vals = {'Ultra': 1, 'Super': 2, 'Soft': 3, 'Medium': 4,
                'Hard': 5, 'Intermediate': 6}
    return vals[tire]




# Create a list of the available races to date that we can use for training
races = os.listdir('data/fia')
races = races[1:]

# Create DataFrame of all laps for all drivers in all races
list_of_times = []
for race in races:
    lap_times = f1.create_race_features(race)
    list_of_times.append(lap_times)
    print '{} complete.'.format(race)
all_lap_times = pd.concat(list_of_times)
all_lap_times.reset_index(inplace=True, drop=True)

# Add column to classify laps race under Safety Car
all_lap_times['SAFETY'] = all_lap_times.apply(
        lambda x: f1.assign_safety(x['TRACK'], x['YEAR'], x['LAP']), axis=1)

# Add Stints column to count laps since last tire change
all_lap_times = f1.assign_stint_lap(all_lap_times)

# Remove pit laps and out laps, remove safety laps, remove starting lap
no_pits = f1.remove_pits(all_lap_times)
no_pits.drop(no_pits[no_pits['LAP'] == 1].index, axis=0, inplace=True)
no_safety = no_pits[no_pits['SAFETY'] == 0]

# Load Track Data
track_data = f1.load_tracks(features=False)
track_data.drop(['T_TEMP_MIN'], axis=1, inplace=True)

# Create full feature dataframe
lap_features = pd.merge(no_safety, track_data, how='left', on=['TRACK', 'YEAR'])
regression_features = lap_features.drop(['NO', 'GAP', 'TRACK', 'YEAR', 'RACE', 'SAFETY'], axis=1)
regression_dummies = pd.get_dummies(regression_features, columns=['TIRE'])
regression_dummies.drop('TIRE_Intermediate', axis=1, inplace=True)
# print regression_dummies
# print regression_dummies.info()

# Create feature matrix, targets, train_test_split
y = regression_dummies.pop('TIME')
X = regression_dummies
X_train, X_test, y_train, y_test = train_test_split(X, y)

# Linear Regression Model
model_train = sms.OLS(y_train, sms.add_constant(X_train)).fit()
summary = model_train.summary()
print summary

# Random Forest Regressor
rfr = RandomForestRegressor(n_estimators=20, max_features='sqrt', oob_score=True)
rfr.fit(X_train, y_train)
rfr.oob_score_
rfr.score(X_train, y_train)
print 'Test Score: ', rfr.score(X_test, y_test)

# Train model with full dataset for pickeling
model = sms.OLS(y, sms.add_constant(X)).fit()
with open('scripts/model.pickle', 'wb') as f:
    pickle.dump(model, f)
