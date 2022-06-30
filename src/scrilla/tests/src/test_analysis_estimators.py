import pytest
import math
import random

from scrilla.analysis import estimators
from scrilla.util.errors import SampleSizeError

from .. import mock_data
from .. import settings


@pytest.mark.parametrize("x", [(mock_data.univariate_data[datum]) for datum in mock_data.univariate_data])
def test_univariate_normal_likelihood_probability_bounds(x):
    sample_mean = estimators.sample_mean(x)
    sample_variance = estimators.sample_variance(x)
    likelihood = math.exp(estimators.univariate_normal_likelihood_function(
        [sample_mean, sample_variance], x))
    assert(likelihood > 0 and likelihood < 1)


@pytest.mark.parametrize("x", [(mock_data.univariate_data[datum]) for datum in mock_data.univariate_data])
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
    #                                                                              all include the event of
    #                                                                              observing (1, 2)
    #
    #       is this true? isn't observing two random elements from a sample a different type of thing than
    #       observing three random elements? or can we say, the probability the third element is something
    #       from the sample is 1, so the probability of the sequence (1, 2) is equal to the probability
    #       (1, 2, x) where x represents all possible values of the third element from the population?
    #
    #       does the equivalence of probability imply these two events are the same event? is the probability
    #       of all possible future events embedded in the probability of a sequence, if it is understood
    #       the sequence is generated by identical random draws from the same population?
    assert(likelihood_truncated > likelihood_whole)


@pytest.mark.parametrize("x,y", [(mock_data.bivariate_data[datum]) for datum in mock_data.bivariate_data])
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


@pytest.mark.parametrize("x,mu", mock_data.mean_cases)
def test_mean(x, mu):
    mean = estimators.sample_mean(x=x)
    assert(settings.is_within_tolerance(lambda: mean - mu))


@pytest.mark.parametrize("x", [([])])
def test_mean_null_sample(x):
    with pytest.raises(Exception) as sample_error:
        estimators.sample_mean(x=x)
    assert sample_error.type == SampleSizeError


@pytest.mark.parametrize("x", [
    ([None]),
    ([1, 2, None]),
])
def test_mean_missing_samples(x):
    with pytest.raises(Exception) as sample_error:
        estimators.sample_mean(x=x)
    assert sample_error.type == ValueError


@pytest.mark.parametrize("first_x,second_x", mock_data.recursive_univariate_data)
def test_rolling_recursive_mean(first_x, second_x):
    lost_obs, new_obs = first_x[0], second_x[-1]
    n = len(first_x)
    actual_previous_mean = estimators.sample_mean(first_x)
    actual_next_mean = estimators.sample_mean(second_x)
    recursive_mean = estimators.recursive_rolling_mean(
        actual_previous_mean, new_obs, lost_obs, n)
    assert(settings.is_within_tolerance(
        lambda: recursive_mean - actual_next_mean))


@pytest.mark.parametrize("x,var", mock_data.variance_cases)
def test_variance(x, var):
    variance = estimators.sample_variance(x)
    assert(settings.is_within_tolerance(lambda: variance - var))

@pytest.mark.parametrize("x,var", mock_data.variance_cases)
def test_recursive_sum_of_squares(x, var):
    variance = estimators.recursive_sum_of_squares(x)/(len(x) -1)
    assert(settings.is_within_tolerance(lambda:variance - var))

@pytest.mark.parametrize("x", [([])])
def test_variance_null_sample(x):
    with pytest.raises(Exception) as sample_error:
        estimators.sample_variance(x)
    assert sample_error.type == SampleSizeError

@pytest.mark.parametrize("x", [([1]), ([2])])
def test_variance_small_sample(x):
    assert estimators.sample_variance(x) == 0

@pytest.mark.parametrize("x", [([None])])
def test_variance_null_sample(x):
    with pytest.raises(Exception) as sample_error:
        estimators.sample_variance(x)
    assert sample_error.type == ValueError


@pytest.mark.parametrize("first_x,second_x", mock_data.recursive_univariate_data)
def test_rolling_recursive_variance(first_x, second_x):
    lost_obs, new_obs = first_x[0], second_x[-1]
    n = len(first_x)
    actual_previous_mean = estimators.sample_mean(first_x)
    actual_previous_variance = estimators.sample_variance(first_x)
    actual_next_variance = estimators.sample_variance(second_x)
    recursive_variance = estimators.recursive_rolling_variance(
        actual_previous_variance, actual_previous_mean, new_obs, lost_obs, n)
    assert(settings.is_within_tolerance(
        lambda: recursive_variance - actual_next_variance))


@pytest.mark.parametrize("x,y,cov", mock_data.covariance_cases)
def test_covariance(x, y, cov):
    covariance = estimators.sample_covariance(x=x, y=y)
    assert(settings.is_within_tolerance(lambda: covariance - cov))


@pytest.mark.parametrize("x,y,correl", mock_data.correlation_cases)
def test_correlation(x, y, correl):
    correlation = estimators.sample_correlation(x=x, y=y)
    assert(settings.is_within_tolerance(lambda: correlation - correl))


@pytest.mark.parametrize("x,y", [
    ([random.randint(0, 100) for _ in range(99)],
     [random.randint(0, 100) for _ in range(99)]),
    ([random.randint(0, 100) for _ in range(99)],
     [random.randint(0, 100) for _ in range(99)]),
    ([random.randint(0, 100) for _ in range(99)],
     [random.randint(0, 100) for _ in range(99)]),
    ([random.randint(0, 100) for _ in range(99)],
     [random.randint(0, 100) for _ in range(99)])
]
)
def test_correlation_bounds(x, y):
    correlation = estimators.sample_correlation(x=x, y=y)
    assert(abs(correlation) > 0 and abs(correlation) < 1)


@pytest.mark.parametrize("x,y,beta", [(case[0], case[1], case[3])for case in mock_data.regression_cases])
def test_simple_regression_slope(x, y, beta):
    slope = estimators.simple_regression_beta(x=x, y=y)
    assert(settings.is_within_tolerance(lambda: slope - beta))


@pytest.mark.parametrize("x,y,alpha", [(case[0:3]) for case in mock_data.regression_cases])
def test_simple_regression_intercept(x, y, alpha):
    intercept = estimators.simple_regression_alpha(x=x, y=y)
    assert(settings.is_within_tolerance(lambda: intercept - alpha))