import math
import os

import numpy
import pandas




def convert_from_polar_to_cartesian(data) -> pandas.DataFrame:
    data['angle'] = convert_deg_to_rad(data['angle'])
    data['angle'] = set_vertical_to_zero_angle(data['angle'])

    data['x'] = numpy.cos(data['angle']) * data['distance']
    data['y'] = -numpy.sin(data['angle']) * data['distance']

    return data[['x', 'y']]


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


def set_center_to_180_deg(data_polar):
    data_polar.loc[:, 'angle'] += 180
    data_polar.loc[data_polar['angle'] > 360, 'angle'] -= 360

    return data_polar


def main():
    step_size = 1

    spand_dir = 'spand_measurements_test_1'
    for file in os.listdir(spand_dir):
        file_path_in = os.path.join(spand_dir, file)
        file_path_out = os.path.join(spand_dir + '_cartesian', file.replace('.csv', '_cartesian.csv'))

        data_polar = read_raw_scan_file(file_path_in)
        data_polar = set_center_to_180_deg(data_polar)

        max_distance = 1800
        data_polar = data_polar.loc[data_polar['distance'] < max_distance]

        data_polar = interpolate(data_polar, step_size)

        data_cartesian = convert_from_polar_to_cartesian(data_polar)
        data_cartesian['z'] = 0.0

        data_cartesian.loc[(data_cartesian['x'].abs() < 0.001), 'x'] = 0
        data_cartesian.loc[(data_cartesian['y'].abs() < 0.001), 'y'] = 0

        data_cartesian *= 0.1
        data_cartesian.to_csv(file_path_out, header=False, index=False)


if __name__ == '__main__':
    main()
