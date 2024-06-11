import numpy as np
from scipy.stats import binom, norm


def exponential_decay(theta):
    # theta determines the level of top-weightedness.
    def f(depth, n):
        d = depth - 1  # depth is 1 indexed while the function is 0 indexed

        k = (-n / 4 * np.log(0.3))

        exp_term = np.exp(-1 * (d / k))

        return (theta * exp_term)

    return f


def logarithmic_growth():
    # theta determines the level of top-weightedness.
    def f(depth, n):

        return np.log(depth) / np.log(n + 1)

    return f


def gaussian_distribution(mean, std_dev):
    def f(depth, n):
        d = depth
        gaussian = norm(loc=mean, scale=std_dev)

        scale = gaussian.pdf(mean)

        return gaussian.pdf(d) / scale

    return f


def uniform():
    def f(depth, n):
        return depth / n

    return f

def scaled_binomial(p):
    def f(depth, n):
        largest_probability_x = n * p
        scale_factor = 1 / binom.pmf(largest_probability_x, n, p)
        return scale_factor * binom.pmf(depth, n, p)

    return f
