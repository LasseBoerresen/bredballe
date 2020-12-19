import math
import os

import numpy
import pandas
# import plotly
import matplotlib.pyplot as plt
from matplotlib.pyplot import show, polar
import numpy as np


def convert_from_polar_to_cartesian(data, *, flip_left_right=False) -> pandas.DataFrame:
    data = data.copy()
    data['angle'] = convert_deg_to_rad(data['angle'])
    data['angle'] = set_vertical_to_zero_angle(data['angle'])

    x_direction = 1
    if flip_left_right:
        x_direction = -1

    data['x'] = x_direction * numpy.cos(data['angle']) * data['distance']
    data['y'] = numpy.sin(data['angle']) * data['distance']

    data = set_zero_exact(data)

    return data[['x', 'y']]


def set_zero_exact(data):
    data.loc[(data['x'].abs() < 0.001), 'x'] = 0
    data.loc[(data['y'].abs() < 0.001), 'y'] = 0

    return data


def set_vertical_to_zero_angle(data):
    return data - math.tau / 4


def convert_deg_to_rad(data):
    return data * math.tau / 360


def interpolate(data_polar: pandas.DataFrame, step_size):

    data_polar = data_polar.set_index('angle')
    data_polar = data_polar.sort_index()

    resampled_index = create_resampled_index(data_polar, step_size)
    for angle in resampled_index:
        data_polar.loc[angle, 'distance'] = numpy.nan
    data_polar = data_polar.sort_index()
    data_polar = data_polar.interpolate()

    data_polar = data_polar.loc[resampled_index]
    data_polar = data_polar.reset_index()

    data_polar = data_polar.dropna(axis=0)

    return data_polar


def create_resampled_index(data_polar, step_size):
    return numpy.arange(
        (data_polar.index.min() - data_polar.index.min() % 10),
        data_polar.index.max(),
        step_size)


def read_raw_scan_file(file_path_in) -> pandas.DataFrame:
    data_polar = pandas.read_csv(
        file_path_in, sep=' ', header=None, skiprows=3)
    data_polar.columns = ['angle', 'distance', 'quality']
    return data_polar


def set_center_to_180_deg(data):
    data = data.copy()
    data += 180
    data.loc[data > 360] -= 360

    return data


def to_fusion_csv(data_cartesian, file_path_out):
    data_cartesian.loc['z'] = 0.0
    data_cartesian *= 0.1
    data_cartesian.to_csv(file_path_out, header=False, index=False)


def cut_distances(data_polar, min, max):
    data_polar = data_polar.loc[
        (data_polar['distance'] > min)
        & (data_polar['distance'] < max)]

    return data_polar


def cut_extreme_angles(data, min, max):
    return data.loc[(data['angle'] >= min) & (data['angle'] <= max)]


def main():
    # pandas.options.plotting.backend = "plotly"
    step_size = 1

    deck_restrictions = pandas.DataFrame(
        columns=['file', 'angle', 'distance_min', 'distance_max', 'flip_lr'],
        data=[
            ['1_40.csv',  25, 1300, 1600, False],
            ['2_35.csv',  35, 1250, 1700, False],
            ['3_80.csv',  45, 1250, 2000, False],
            ['4_00.csv',  45, 1200, 2000, False],
            ['4_20.csv',  45, 1100, 2000, False],
            ['5_20.csv',  47, 1000, 2200, False],
            ['5_30.csv',  47,  900, 2200, False],
            ['6_25.csv',  50,  900, 2400, True],
            ['7_35.csv',  50,  900, 2400, True],
            ['7_45.csv',  50,  900, 2400, True],
            ['8_34.csv',  50,  900, 2500, True],
            ['8_55.csv',  50, 1550, 2600, True],
            ['9_35.csv',  50, 1550, 2500, True],
            ['10_15.csv', 45, 1600, 2400, True],
            ['10_32.csv', 45, 1600, 2400, True],
            ['10_75.csv', 45, 1600, 2400, True],
            ['10_82.csv', 45, 1600, 2400, True],
            ['11_35.csv', 45, 1500, 2400, True]])
    deck_restrictions = deck_restrictions.set_index('file')

    spand_dir = 'spand_measurements_deck'
    skip = True
    for file in deck_restrictions.index:
        if file == '1_40.csv':
            skip = False

        if skip:
            continue

        file_path_in = os.path.join(spand_dir, file)
        file_path_out = os.path.join(
            spand_dir + '_cartesian', file.replace('.csv', '_cartesian.csv'))

        cut_angle = deck_restrictions.loc[file, 'angle']
        cut_distance_min = deck_restrictions.loc[file, 'distance_min']
        cut_distance_max = deck_restrictions.loc[file, 'distance_max']

        data_polar = read_raw_scan_file(file_path_in)
        data_polar['angle'] = set_center_to_180_deg(data_polar.copy()['angle'])
        data_polar = data_polar.sort_values(by='angle')
        # data_polar = cut_distances(data_polar, cut_distance_min, 2800)

        plot(data_polar, file)

        data_polar = cut_distances(data_polar, cut_distance_min, cut_distance_max)
        data_polar = cut_extreme_angles(data_polar, min=180-cut_angle, max=180+cut_angle)

        plot(data_polar, file)
        pass

        # interpolate early just to get better overview
        # data_polar = interpolate(data_polar, step_size)


        # data_polar_start = data_polar.iloc[:30]
        # data_polar_end = data_polar.iloc[-30:]
        # data_polar_to_interploate = data_polar.iloc[30:-30]
        # data_polar_to_interploate = data_polar
        # data_polar_to_interploate = interpolate(data_polar_to_interploate, step_size)
        # data_polar = pandas.concat([data_polar_start, data_polar_to_interploate, data_polar_end])
        data_cartesian = convert_from_polar_to_cartesian(data_polar)

        to_fusion_csv(data_cartesian, file_path_out)


def plot(data_polar, file):
    ax = plt.subplot(111, projection='polar')
    ax.scatter(
        convert_deg_to_rad(data_polar['angle'].values),
        data_polar['distance'].values, )
    ax.set_rmax(5000)
    ax.set_rticks(range(0, 2500, 200))
    lines, labels = plt.thetagrids(range(0, 360, 10))
    ax.set_rlabel_position(-200)
    ax.set_title(file, va='bottom')
    show()


if __name__ == '__main__':
    main()
