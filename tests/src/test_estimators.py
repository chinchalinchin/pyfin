import pytest
import math
import random

from scrilla.static import constants
from scrilla.analysis import estimators

univariate_data = {
    'case_1': [16, -12, -17, 1, -3, -4, 17, 0, -14, 16],
    'case_2':  [53, 73, 49, 3, 2, 24, 29, 69, 24, 96],
    'case_3': [73, 71, 3, 4, 42, 52, 34, 32, 21, 39],
    'case_4': [77, 74, 64, 49, 31, 7, 35, 46, 15, 70],
    'case_5': [21, 8, 30, 62, 47, 29, 38, 71, 78, 7]
}
recursive_univariate_data = [
    (univariate_data['case_1'][:-1], univariate_data['case_1'][1:]),
    (univariate_data['case_2'][:-1], univariate_data['case_2'][1:]),
    (univariate_data['case_3'][:-1], univariate_data['case_3'][1:]),
    (univariate_data['case_4'][:-1], univariate_data['case_4'][1:]),
    (univariate_data['case_5'][:-1], univariate_data['case_5'][1:]),
]
bivariate_data = {
    'case_1': (univariate_data['case_1'], univariate_data['case_2']),
    'case_2': (univariate_data['case_1'], univariate_data['case_3']),
    'case_3': (univariate_data['case_1'], univariate_data['case_4']),
    'case_4': (univariate_data['case_1'], univariate_data['case_5'])
}

mean_cases = [
    (univariate_data['case_1'], 0),
    (univariate_data['case_2'], 42.2),
    (univariate_data['case_3'], 37.1),
    (univariate_data['case_4'],  46.8),
    (univariate_data['case_5'],  39.1),
]
variance_cases = [
    (univariate_data['case_1'], 161.777777777778),
    (univariate_data['case_2'], 968.177777777778),
    (univariate_data['case_3'], 582.322222222222),
    (univariate_data['case_4'],  608.4),
    (univariate_data['case_5'],  625.433333333333),
]
covariance_cases = [
    (bivariate_data['case_1'][0],
     bivariate_data['case_1'][1], 81.4444444444444),
    (bivariate_data['case_2'][0],
     bivariate_data['case_2'][1], 93.6666666666667),
    (bivariate_data['case_3'][0],
     bivariate_data['case_3'][1], 76.5555555555556),
    (bivariate_data['case_4'][0],
     bivariate_data['case_4'][1], -88.7777777777778),
]
correlation_cases = [
    (bivariate_data['case_1'][0],
     bivariate_data['case_1'][1], 0.205790099581043),
    (bivariate_data['case_2'][0],
     bivariate_data['case_2'][1], 0.305171484680075),
    (bivariate_data['case_3'][0],
     bivariate_data['case_3'][1], 0.244018457215175),
    (bivariate_data['case_4'][0],
     bivariate_data['case_4'][1], -0.279096458172889),

]
# alpha, beta
regression_cases = [
    (bivariate_data['case_1'][0], bivariate_data['case_1']
     [1], 42.2, 0.503434065934066),
    (bivariate_data['case_2'][0], bivariate_data['case_2']
     [1], 37.1, 0.578983516483516),
    (bivariate_data['case_3'][0], bivariate_data['case_3']
     [1], 46.8, 0.473214285714286),
    (bivariate_data['case_4'][0], bivariate_data['case_4']
     [1], 39.1, -0.548763736263736),
]


def is_within_tolerance(func):
    return (abs(func()) < 10 ** (-constants.constants['ACCURACY']))


@pytest.mark.parametrize("x", [(univariate_data[datum]) for datum in univariate_data])
def test_univariate_normal_likelihood_probability_bounds(x):
    sample_mean = estimators.sample_mean(x)
    sample_variance = estimators.sample_variance(x)
    likelihood = math.exp(estimators.univariate_normal_likelihood_function(
        [sample_mean, sample_variance], x))
    assert(likelihood > 0 and likelihood < 1)


@pytest.mark.parametrize("x", [(univariate_data[datum]) for datum in univariate_data])
def test_univariate_normal_likelihood_monotonicity(x):
    """
    Assume the samples are populations, then sample mean is population mean. The sample mean of the 
    truncated sample is distributed around the sample mean of the population. In other words, observations 
    from the population and the truncated sample have the same distribution. Therefore, by the monotonicity
    of probability distributions, the probability of the truncated sample should be less than the probability
    of the entire population.
    """
    sample_mean = estimators.sample_mean(x)
    sample_variance = estimators.sample_variance(x)
    likelihood_whole = math.exp(estimators.univariate_normal_likelihood_function([
                                sample_mean, sample_variance], x))

    likelihood_truncated = math.exp(estimators.univariate_normal_likelihood_function([
                                    sample_mean, sample_variance], x[:-2]))

    # NOTE:
    #   Proposition
    #       the event of the whole sample is a subset of the event of the truncated sample
    #
    #   Notes
    #       observing the sequence (1, 2, 3) is a subset of observing the sequence (1, 2)
    #                                                                         e.g. (1, 2, 3)
    #                                                                              (1, 2, 75),
    #                                                                              (1, 2, -6), etc.
    #
    #       is this true? isn't observing two random elements from a sample a different type of thing than
    #       observing three random elements? or can we say, the probability the third element is something
    #       from the sample is 1, so the probability of the sequence (1, 2) is equal to the probability
    #       (1, 2, x) where x represents all possible values of the third element from the population?
    #
    #       does the equivalence of probability imply these two events are the same event? is the probability
    #       of all possible future events embedded in the probability of a sequence, if it is understood
    #       the sequence is generated identical random draws from the same population?
    assert(likelihood_truncated > likelihood_whole)


@pytest.mark.parametrize("x,y", [(bivariate_data[datum]) for datum in bivariate_data])
def test_bivariate_normal_likelihood_probability_bounds(x, y):
    sample_x_mean_whole = estimators.sample_mean(x)
    sample_x_var_whole = estimators.sample_variance(x)
    sample_y_mean_whole = estimators.sample_mean(y)
    sample_y_var_whole = estimators.sample_variance(y)
    sample_xy_cov_whole = estimators.sample_covariance(x, y)
    data = [[sample_x, y[i]] for i, sample_x in enumerate(x)]
    params = [sample_x_mean_whole, sample_y_mean_whole, sample_x_var_whole,
              sample_y_var_whole, sample_xy_cov_whole]
    likelihood_whole = math.exp(
        estimators.bivariate_normal_likelihood_function(params, data))

    sample_x_mean_truncated = estimators.sample_mean(x)
    sample_x_var_truncated = estimators.sample_variance(x)
    sample_y_mean_truncated = estimators.sample_mean(y)
    sample_y_var_truncated = estimators.sample_variance(y)
    sample_xy_cov_truncated = estimators.sample_covariance(x, y)
    data = [[sample_x, y[i]] for i, sample_x in enumerate(x[:-2])]
    params = [sample_x_mean_truncated, sample_y_mean_truncated, sample_x_var_truncated,
              sample_y_var_truncated, sample_xy_cov_truncated]
    likelihood_truncated = math.exp(
        estimators.bivariate_normal_likelihood_function(params, data))

    # NOTE: see note in previous test.
    assert(likelihood_truncated > likelihood_whole)


@pytest.mark.parametrize("x,mu", mean_cases)
def test_mean(x, mu):
    mean = estimators.sample_mean(x=x)
    assert(is_within_tolerance(lambda: mean - mu))


@pytest.mark.parametrize("first_x,second_x", recursive_univariate_data)
def test_rolling_recursive_mean(first_x, second_x):
    lost_obs, new_obs = first_x[0], second_x[-1]
    n = len(first_x)
    actual_previous_mean = estimators.sample_mean(first_x)
    actual_next_mean = estimators.sample_mean(second_x)
    recursive_mean = estimators.recursive_rolling_mean(
        actual_previous_mean, new_obs, lost_obs, n)
    assert(is_within_tolerance(lambda: recursive_mean - actual_next_mean))


@pytest.mark.parametrize("x,var", variance_cases)
def test_variance(x, var):
    variance = estimators.sample_variance(x)
    assert(is_within_tolerance(lambda: variance - var))


@pytest.mark.parametrize("first_x,second_x", recursive_univariate_data)
def test_rolling_recursive_variance(first_x, second_x):
    lost_obs, new_obs = first_x[0], second_x[-1]
    n = len(first_x)
    actual_previous_mean = estimators.sample_mean(first_x)
    actual_previous_variance = estimators.sample_variance(first_x)
    actual_next_variance = estimators.sample_variance(second_x)
    recursive_variance = estimators.recursive_rolling_variance(
        actual_previous_variance, actual_previous_mean, new_obs, lost_obs, n)
    assert(is_within_tolerance(lambda: recursive_variance - actual_next_variance))


@pytest.mark.parametrize("x,y,cov", covariance_cases)
def test_covariance(x, y, cov):
    covariance = estimators.sample_covariance(x=x, y=y)
    assert(is_within_tolerance(lambda: covariance - cov))


@pytest.mark.parametrize("x,y,correl", correlation_cases)
def test_correlation(x, y, correl):
    correlation = estimators.sample_correlation(x=x, y=y)
    assert(is_within_tolerance(lambda: correlation - correl))


@pytest.mark.parametrize("x,y", [
    ([random.randint(0, 100) for x in range(99)],
     [random.randint(0, 100) for x in range(99)]),
    ([random.randint(0, 100) for x in range(99)], [
        random.randint(0, 100) for x in range(99)]),
    ([random.randint(0, 100) for x in range(99)], [
        random.randint(0, 100) for x in range(99)]),
    ([random.randint(0, 100) for x in range(99)], [
        random.randint(0, 100) for x in range(99)])
]
)
def test_correlation_bounds(x, y):
    correlation = estimators.sample_correlation(x=x, y=y)
    assert(abs(correlation) > 0 and abs(correlation) < 1)


@pytest.mark.parametrize("x,y,beta", [(case[0], case[1], case[3])for case in regression_cases])
def test_simple_regression_slope(x, y, beta):
    slope = estimators.simple_regression_beta(x=x, y=y)
    assert(is_within_tolerance(lambda: slope - beta))


@pytest.mark.parametrize("x,y,alpha", [(case[0:3]) for case in regression_cases])
def test_simple_regression_intercept(x, y, alpha):
    intercept = estimators.simple_regression_alpha(x=x, y=y)
    assert(is_within_tolerance(lambda: intercept - alpha))