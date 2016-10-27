import random


def __log_normal(sigma, mean):
    """
    Log normal distribution is an approximation on the 50th percentile
    :param sigma: The larger the value, the longer the tail
    :param mean: The 50th percentile of latencies
    :return: the log normal value
    """
    return float(round(random.gauss(mean, sigma)))


def __random(a, b):
    """
    Generates a random number within the range a, b
    :param a: random from
    :param b: random to
    :return: a random value in range
    """
    return float(random.randint(a, b))
