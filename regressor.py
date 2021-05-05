import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import autokeras as ak

from sklearn.model_selection import train_test_split

from src.generate_data import get_samples, calculate_next_closing_price

from timeit import default_timer as timer


def get_datasets(time_series_path, feature_length, output_length, train_size, label_function):
    """ Get training and validation feature and label sets.

    :param time_series_path: path to time series
    :param feature_length: number of past values to use for prediction
    :param output_length: number of future values to predict
    :param train_size: size of training set
    :param label_function: function to calculate the label
    :return: x_train, x_test, y_train, y_test
    """
    # load time series
    time_series = pd.read_csv(time_series_path)

    # extract samples
    features, labels = get_samples(time_series, feature_length, output_length, label_function)

    # split samples
    x_train, x_test, y_train, y_test = train_test_split(features, labels, train_size=train_size)

    return x_train, x_test, y_train, y_test


def normalize_data(data, mean=None, std=None):
    """ Normalize data by calculating the Z-score.

    :param data: data set not flattened
    :param mean: array of mean of all columns of training data, if None then find the mean in the data set
    :param std: array of std of all columns of training data, if None then find the std in the data set
    :return: data, mean, std
    """
    if mean is None or std is None:
        # stack samples
        stacked = np.vstack((sample for sample in data))
        mean = stacked.mean(axis=0)
        std = stacked.std(axis=0)

    # normalize samples
    for sample in range(len(data)):
        data[sample] = (data[sample] - mean) / std

    return data, mean, std


def main():
    # paths
    # path to time series
    time_series_path = '../output/dataframes/BTCUSDT/BTCUSDT_m_15.csv'
    # model output path
    model_path = '../output/models/model.h5'

    # data settings
    # number of candles to use as features
    feature_length = 25
    # number of candles to predict
    output_length = 1
    # share of training data from all samples
    train_size = 0.8
    # label function
    label = calculate_next_closing_price

    # model settings
    # number of models to test
    max_trials = 300

    # load data sets
    print('Loading data sets...')
    x_train, x_test, y_train, y_test = get_datasets(time_series_path, feature_length, output_length, train_size, label)

    # normalize data
    x_train, mean, std = normalize_data(x_train)
    x_test = normalize_data(x_test, mean, std)[0]

    # flatten features
    x_train = np.array([x_train[i].flatten() for i in range(len(x_train))])
    x_test = np.array([x_test[i].flatten() for i in range(len(x_test))])

    start_time = timer()

    # get model
    model = ak.StructuredDataRegressor(max_trials=max_trials)
    model.fit(x_train, y_train)

    print(f'Evaluation: {model.evaluate(x_test, y_test)}')

    print(f'Done getting model after {timer() - start_time}s!')

    model = model.export_model()
    model.save(model_path)
    print(f'Model saved in {model_path}')


if __name__ == '__main__':
    main()
