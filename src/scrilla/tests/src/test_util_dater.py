import pytest

from scrilla.util import dater


@pytest.mark.parametrize('start_date,days,bond,result', [
    ('2021-11-15', 2, False, '2021-11-11'),
    ('2021-10-19', 5, False, '2021-10-12'),
    ('2021-09-13', 7, False, '2021-09-01'),  # includes labor day
    ('2021-11-24', 10, False, '2021-11-10'),
    ('2021-06-01', 2, False, '2021-05-27'),  # includes memorial day,
    ('2022-06-22', 1, False, '2022-06-17') # includes first observance of Juneteenth
])
def test_decrement_date_by_business_days(start_date, days, bond, result):
    test_date = dater.decrement_date_by_business_days(start_date, days, bond)
    assert(test_date == dater.parse(result))


@pytest.mark.parametrize('start_date,end_date,length', [
    ('2021-11-04', '2021-11-06', 3),
    ('2020-01-01', '2020-02-05', 36)
])
def test_dates_between(start_date, end_date, length):
    date_range = dater.dates_between(start_date, end_date)
    assert(len(date_range) == length)
    assert(dater.parse(start_date) in date_range)
    assert(dater.parse(end_date) in date_range)
