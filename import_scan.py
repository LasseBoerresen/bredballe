import math
import os

import numpy
import pandas


def convert_from_polar_to_cartesian(data, *, flip_left_right=False) -> pandas.DataFrame:
    data['angle'] = convert_deg_to_rad(data['angle'])
    data['angle'] = set_vertical_to_zero_angle(data['angle'])

    x_direction = 1
    if flip_left_right:
        x_direction = -1

    data['x'] = x_direction * numpy.cos(data['angle']) * data['distance']
    data['y'] = numpy.sin(data['angle']) * data['distance']

    set_zero_exact(data)

    return data[['x', 'y']]


def set_zero_exact(data):
    data.loc[(data['x'].abs() < 0.001), 'x'] = 0
    data.loc[(data['y'].abs() < 0.001), 'y'] = 0


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


def to_fusion_csv(data_cartesian, file_path_out):
    data_cartesian['z'] = 0.0
    data_cartesian *= 0.1
    data_cartesian.to_csv(file_path_out, header=False, index=False)


def cut_long_distances(data_polar):
    max_distance = 2000
    data_polar = data_polar.loc[data_polar['distance'] < max_distance]
    return data_polar


def main():
    step_size = 5

    spand_dir = 'spand_measurements'
    for file in os.listdir(spand_dir):
        file_path_in = os.path.join(spand_dir, file)
        file_path_out = os.path.join(
            spand_dir + '_cartesian', file.replace('.csv', '_cartesian.csv'))

        data_polar = read_raw_scan_file(file_path_in)
        data_polar = cut_long_distances(data_polar)
        data_polar_start = data_polar.iloc[:30]
        data_polar_end = data_polar.iloc[-30:]
        data_polar_to_interploate = data_polar.iloc[30:-30]
        data_polar_to_interploate = interpolate(data_polar_to_interploate, step_size)
        data_polar = pandas.concat([data_polar_start, data_polar_to_interploate, data_polar_end])
        data_cartesian = convert_from_polar_to_cartesian(data_polar)

        to_fusion_csv(data_cartesian, file_path_out)


if __name__ == '__main__':
    main()
