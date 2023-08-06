# coding: utf-8

from __future__ import unicode_literals

from nose.plugins.attrib import attr

from box.test.flaky.names import FlakyNames


def flaky(max_runs=None, min_passes=None):
    """
    Decorator used to mark a test as "flaky". When used in conjuction with
    the flaky nosetests plugin, will cause the decorated test to be retried
    until min_passes successes are achieved out of up to max_runs test runs.
    """
    if max_runs is None:
        max_runs = 2
    if min_passes is None:
        min_passes = 1
    if min_passes <= 0:
        raise ValueError('min_passes must be positive')
    if max_runs < min_passes:
        raise ValueError('min_passes cannot be greater than max_runs!')
    return attr(**{
        FlakyNames.MAX_RUNS: max_runs,
        FlakyNames.MIN_PASSES: min_passes,
        FlakyNames.CURRENT_RUNS: 0,
        FlakyNames.CURRENT_PASSES: 0,
    })
