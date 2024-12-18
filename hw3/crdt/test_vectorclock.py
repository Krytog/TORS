import pytest

from vectorclock import *


def test_vectorclock1():
    vectorclock1 = VectorClock(
        {
            1: 1,
            2: 1,
            3: 2,
        }
    )
    vectorclock2 = VectorClock(
        {
            1: 1,
            2: 1,
            3: 1,
        }
    )
    assert vectorclock1.compare_against(vectorclock2) == CompareStatus.After


def test_vectorclock2():
    vectorclock1 = VectorClock(
        {
            1: 1,
            2: 1,
            3: 2,
        }
    )
    vectorclock2 = VectorClock(
        {
            1: 1,
            2: 2,
            3: 3,
        }
    )
    assert vectorclock1.compare_against(vectorclock2) == CompareStatus.Before


def test_vectorclock3():
    vectorclock1 = VectorClock(
        {
            1: 1,
            2: 1,
        }
    )
    vectorclock2 = VectorClock(
        {
            1: 1,
            2: 2,
            3: 3,
        }
    )
    assert vectorclock1.compare_against(vectorclock2) == CompareStatus.Before


def test_vectorclock4():
    vectorclock1 = VectorClock(
        {
            1: 5,
            2: 5,
        }
    )
    vectorclock2 = VectorClock(
        {
            1: 1,
            2: 2,
            3: 3,
        }
    )
    assert vectorclock1.compare_against(vectorclock2) == CompareStatus.Conflict


def test_vectorclock5():
    vectorclock1 = VectorClock(
        {
            1: 5,
            2: 5,
            3: 1,
            4: 2,
        }
    )
    vectorclock2 = VectorClock(
        {
            1: 1,
            2: 2,
        }
    )
    assert vectorclock1.compare_against(vectorclock2) == CompareStatus.After


def test_vectorclock6():
    vectorclock1 = VectorClock(
        {
            1: 1,
            2: 1,
            3: 1,
        }
    )
    vectorclock2 = VectorClock(
        {
            1: 1,
            2: 1,
        }
    )
    assert vectorclock1.compare_against(vectorclock2) == CompareStatus.Same
