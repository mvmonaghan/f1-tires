# import general libraries
import pandas as pd
import numpy as np
import datetime
import os
import cPickle as pickle
import scripts.f1_scripts  as f1
# import ML libraries
import statsmodels.api as sms
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import cross_val_score
# # import plotting libraries
# import matplotlib.pyplot as plt
# import seaborn as sn


if __name__ == '__main__':
    # Create a list of the available races to date to use for model training
    races = os.listdir('data/fia')
    races = races[1:]
    races.pop() #Remove 2016_4_russia until data is available

    # Create DataFrame of all laps for all drivers in all races
    list_of_times = []
    for race in races:
        lap_times = f1.create_race_features(race)
        list_of_times.append(lap_times)
        print '{} complete.'.format(race)
    all_lap_times = pd.concat(list_of_times)
    all_lap_times.reset_index(inplace=True, drop=True)

    # Add column to classify laps raced under Safety Car
    all_lap_times['SAFETY'] = all_lap_times.apply(
            lambda x: f1.assign_safety(x['TRACK'], x['YEAR'], x['LAP']), axis=1)

    # Remove pit laps and out laps, remove safety laps, remove starting lap
    no_pits = f1.remove_pits(all_lap_times)
    no_pits.drop(no_pits[no_pits['LAP'] == 1].index, axis=0, inplace=True)
    no_safety = no_pits[no_pits['SAFETY'] == 0]

    # Get tire dummies
    tire_dummies = pd.get_dummies(no_safety, columns=['TIRE'])
    tire_dummies.drop(['TIRE_INTERMEDIATE'], axis=1, inplace=True)

    # Load Track Data
    track_data = f1.load_tracks(features=False)
    track_data.drop(['T_TEMP_MIN'], axis=1, inplace=True)

    # Create full feature dataframe
    lap_features = pd.merge(tire_dummies, track_data, how='left', on=['TRACK', 'YEAR'])

    # Create feature matrix, targets, train_test_split
    single_model = lap_features.copy()
    single_model = single_model.drop(['NO', 'GAP', 'TRACK', 'YEAR', 'RACE', 'SAFETY', 'LOW_TIRE_WEAR'], axis=1)
    y_single = single_model.pop('TIME')
    X_single = sms.add_constant(single_model)
    X_single_train, X_single_test, y_single_train, y_single_test = train_test_split(X_single, y_single)

    # Linear Regression Model
    model_train = sms.OLS(y_single_train, X_single_train).fit()
    single_summary = model_train.summary(title='Single Model')
    print single_summary


    # Split Data into train, test sets to train and evaluate models
    X = lap_features.copy()     # Fearure matrix
    y = X.pop('TIME')           # Liear Regression Targets
    z = X.pop('LOW_TIRE_WEAR')  # Logistic Regression Targets
    X_train, X_test, y_train, y_test, z_train, z_test = train_test_split(X, y, z)

    # Train Logistic Regression Model to classify High Tire Wear vs. Low Tire Wear
    logit_X_train = X_train[['LENGTH', 'DOWNFORCE', 'LATERAL', 'ASPHALT_ABR',
                                'ASPHALT_GRP', 'TIRE_STRESS', 'AIR_TEMP_MAX',
                                'AIR_TEMP_MIN', 'T_TEMP_MAX']]
    logit_X_test = X_test[['LENGTH', 'DOWNFORCE', 'LATERAL', 'ASPHALT_ABR',
                                'ASPHALT_GRP', 'TIRE_STRESS', 'AIR_TEMP_MAX',
                                'AIR_TEMP_MIN', 'T_TEMP_MAX']]
    logit = LogisticRegression()
    logit.fit(logit_X_train, z_train)
    print 'Tire Ware Model Accuracy:\n', logit.score(logit_X_test, z_test)
    idx = logit_X_test.index[logit.predict(logit_X_test) == 1]
    print 'Tracks with Low Tire Wear Classification:\n', lap_features.ix[idx]['TRACK'].unique()

    # Pickle Tire Wear Classifier for use in RaceSimulator
    with open('scripts/tire_wear_classifier.pickle', 'wb') as f:
        pickle.dump(logit, f)



    # Create feature matrix, targets, train_test_split for Low Tire Wear model
    low_tire_wear = lap_features[lap_features['LOW_TIRE_WEAR'] == 1]
    low_regression_features = low_tire_wear.drop(['NO', 'GAP', 'TRACK', 'YEAR', 'RACE', 'SAFETY', 'LOW_TIRE_WEAR'], axis=1)
    low_y = low_regression_features.pop('TIME')
    low_X = sms.add_constant(low_regression_features)
    low_X.drop('STINT_LAP', axis=1, inplace=True)
    low_X_train, low_X_test, low_y_train, low_y_test = train_test_split(low_X, low_y)

    # Linear Regression Model for Low Tire Wear
    low_model_train = sms.OLS(low_y_train, low_X_train).fit()
    low_summary = low_model_train.summary(title='Low Tire Wear Model')
    print low_summary

    # Pickle Tire Wear Model for use in RaceSimulator
    with open('scripts/low_tire_wear_model.pickle', 'wb') as f:
        pickle.dump(low_model_train, f)

    # Create feature matrix, targets, train_test_split for High Tire Wear model
    high_tire_wear = lap_features[lap_features['LOW_TIRE_WEAR'] == 0]
    high_regression_features = high_tire_wear.drop(['NO', 'GAP', 'TRACK', 'YEAR', 'RACE', 'SAFETY', 'LOW_TIRE_WEAR'], axis=1)
    high_y = high_regression_features.pop('TIME')
    high_X = sms.add_constant(high_regression_features)
    high_X.drop('STINT_LAP', axis=1, inplace=True)
    high_X_train, high_X_test, high_y_train, high_y_test = train_test_split(high_X, high_y)

    # Linear Regression Model
    high_model_train = sms.OLS(high_y_train, high_X_train).fit()
    high_summary = high_model_train.summary(title='High Tire Wear Model')
    print high_summary

    # Pickle Tire Wear Model for use in RaceSimulator
    with open('scripts/high_tire_wear_model.pickle', 'wb') as f:
        pickle.dump(high_model_train, f)
