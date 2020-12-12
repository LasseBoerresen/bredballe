import pandas
import pytest

from import_scan import convert_from_polar_to_cartesian


class TestConvertFromPolarToCartesian:

    tolerance = 1e-6

    def test_given_angle_0_and_dist_0__then_returns_x_0_and_y_0(self):
        data = pandas.DataFrame(columns=['angle', 'distance'], data=[[0, 0]])

        actual = convert_from_polar_to_cartesian(data)

        assert abs(actual.iloc[0].x - 0) < self.tolerance
        assert abs(actual.iloc[0].y - 0) < self.tolerance

    def test_given_angle_0_and_dist_1__then_returns_x_0_and_y_1(self):
        data = pandas.DataFrame(columns=['angle', 'distance'], data=[[0, 1]])

        actual = convert_from_polar_to_cartesian(data)

        assert abs(actual.iloc[0].x - 0) < self.tolerance
        assert abs(actual.iloc[0].y - 1) < self.tolerance

    def test_given_angle_180_and_dist_1__then_returns_x_0_and_y_ne1(self):
        data = pandas.DataFrame(columns=['angle', 'distance'], data=[[180, 1]])

        actual = convert_from_polar_to_cartesian(data)

        assert abs(actual.loc[0, 'x'] - 0) < self.tolerance
        assert abs(actual.loc[0, 'y'] - (-1)) < self.tolerance

    def test_given_angle_90_and_dist_1__then_returns_x_1_and_y_0(self):
        data = pandas.DataFrame(columns=['angle', 'distance'], data=[[90, 1]])

        actual = convert_from_polar_to_cartesian(data)

        assert abs(actual.loc[0, 'x'] - 1) < self.tolerance
        assert abs(actual.loc[0, 'y'] - 0) < self.tolerance

    def test_given_angle_270_and_dist_1__then_returns_x_neg1_and_y_0(self):
        data = pandas.DataFrame(columns=['angle', 'distance'], data=[[270, 1]])

        actual = convert_from_polar_to_cartesian(data)

        assert abs(actual.loc[0, 'x'] - (-1)) < self.tolerance
        assert abs(actual.loc[0, 'y'] - 0) < self.tolerance


class TestImportScan:
    def test_create_single_point(self):
        raise NotImplementedError


if __name__ == '__main__':
    pytest.main()
