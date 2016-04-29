import pandas as pd
import numpy as np
import datetime
import os
import cPickle as pickle
from collections import defaultdict
import scripts.f1_scripts  as f1


class Track(object):
    def __init__(self):
        self.track = track
        self.features = None

    def fit(self, track, air_temp_min, air_temp_max, track_temp):
        self.track = track
        tracks = f1.load_tracks()
        tracks['AIR_TEMP_MAX'] = air_temp_max
        tracks['AIR_TEMP_MIN'] = air_temp_min
        tracks['T_TEMP_MAX'] = track_temp
        self.features = tracks[tracks['TRACK'] == self.track]


class DriverStrategy(object):
    def __init__(self):
        self.features = None

    def fit(self, strategy):
        """Convert list of tuples into Series"""
        tires = []
        stint_laps = []
        for tire, lap_count in strategy:
            stint_count = 1
            for lap in xrange(lap_count):
                tires.append(tire)
                stint_laps.append(stint_count)
                stint_count += 1
        laps = np.arange(1, len(tires) + 1, 1)
        self.features = pd.DataFrame({'TIRE': tires, 'LAP': laps, 'STINT_LAP': stint_laps})




class RaceSim(object):
    def __init__(self, estimator, strategy, track, air_temp_min, air_temp_max, track_temp):
        self.estimator = estimator
        self.strategy = strategy
        self.params = estimator.params
        self.track = track
        self.air_temp_min = air_temp_min
        self.air_temp_max = air_temp_max
        self.track_temp = track_temp
        self.estimator = estimator
        self.features = None

    def build_strategy(self):
        driver = DriverStrategy()
        driver.fit(self.strategy)
        driver_features = driver.features
        driver_features['TRACK'] = self.track
        track = Track()
        track.fit(self.track, self.air_temp_min, self.air_temp_max, self.track_temp)
        track_features = track.features
        self.features = pd.merge(driver_features, track_features, how='left', on='TRACK')
        self.features.drop('TRACK', axis=1, inplace=True)




if __name__ == '__main__':
    with open('model.pickle', 'rb') as f:
        model = pickle.load(f)
