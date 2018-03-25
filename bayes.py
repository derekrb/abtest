#!/usr/bin/env python

'''
inspired by: https://cdn2.hubspot.net/hubfs/310840/VWO_SmartStats_technical_whitepaper.pdf
'''

import numpy as np

import abtest


class Exponential:

    def __init__(self, values, frequencies, alpha=0, beta=0):

        if len(values) != len(frequencies):
            raise ValueError('values and frequencies must be of equal length')

        self.alpha = alpha + sum(values)
        self.theta = 1.0 / (
            beta + sum([i[0] * i[1] for i in zip(values, frequencies)])
        )

    def sample_posterior(self, n_samples):
        return np.random.gamma(
            self.alpha,
            scale=self.theta,
            size=n_samples
        )


class Pareto(Exponential):

    def __init__(self, values, frequencies, alpha=0, beta=0, xmin=1):

        if len(values) != len(frequencies):
            raise ValueError('values and frequencies must be of equal length')

        self.alpha = alpha + sum(values)
        self.theta = 1.0 / (
            beta + sum(
                i[0] * np.log(i[1] / float(xmin))
                for i in zip(values, frequencies)
                if i[1] >= xmin
            )
        )


class Bernoulli:

    def __init__(self, alpha, beta, trials, successes):
        self.alpha = alpha + successes
        self.beta = beta + trials - successes

    def sample_posterior(self, n_samples):
        return np.random.beta(
            self.alpha,
            self.beta,
            size=n_samples
        )


class Variant:

    def __init__(self, name, distributions):
        self.name = name
        self.distributions = distributions

    def sample_posterior(self, n_samples):
        self.samples = np.ones(n_samples)
        for distribution in self.distributions:
            self.samples *= distribution.sample_posterior(n_samples)


class Test:

    def __init__(self, variants=None, **kwargs):
        # variants[0] is taken to be control!
        self.variants = variants

        # 1M samples means loss function accurate to ~0.003 (p=(1 - 10^-10))
        self.n_samples = 1000000
        self.min_loss = 0.003
        self.check_every = 500
        self.done = False
        self.winner = None
        self.verbose = kwargs.get('verbose', True)

    def sample_variants(self):
        self.samples = np.empty([len(self.variants), self.n_samples])
        for i, variant in enumerate(self.variants):
            variant.sample_posterior(self.n_samples)
            self.samples[i, :] = variant.samples

    def compute_statistics(self):
        for variant in self.variants:

            variant.beats_control = np.sum(
                np.greater(
                    variant.samples,
                    self.variants[0].samples
                )
            ) / float(self.n_samples)
            variant.beats_all = np.sum(
                np.equal(
                    variant.samples,
                    np.amax(self.samples, axis=0)
                )
            ) / float(self.n_samples)
            variant.loss = np.sum(
                np.amax(
                    self.samples - np.tile(
                        variant.samples, (len(self.variants), 1)
                    ),
                    axis=0
                )
            ) / float(self.n_samples)

    def run(self, abtest):
        self.abtest = abtest

        while not self.done:
            self.abtest.trial()
            
            if self.abtest.trials % self.check_every == 0:

                self.variants = [
                    Variant(l.name, 1, 1, l.trials, l.successes)
                    for l in self.abtest.legs
                ]

                self.report()

    def report(self):
        self.sample_variants()
        self.compute_statistics()

        best_beats_all = 0
        best_leg = None
        for variant in self.variants:

            if self.verbose:
                print(
                    'Variant {} has loss {}, beats control with p={}, '
                    'beats all with p={}'.format(
                    variant.name,
                    np.round(variant.loss, 5),
                    np.round(variant.beats_control, 3),
                    np.round(variant.beats_all, 3)
                    )
                )

            if variant.loss < self.min_loss:
                self.done = True

            if variant.beats_all > best_beats_all:
                best_beats_all = variant.beats_all
                best_leg = variant

        if self.done:

            if not best_leg:
                best_leg = self.variants[0]

            self.winner = best_leg.name

        if self.verbose:
            print(
                'Test finished={}, best leg={}'.format(
                self.done,
                best_leg.name
                )
            )


def main():

    variants = [
        Variant(
            'control',
            [
                Exponential([1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 20, 23], [1129, 67, 43, 16, 10, 1, 5, 2, 4, 1, 1, 1, 1])
            ]
        ),
        Variant(
            'treatment',
            [
                Exponential([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, 18, 19], [1081, 66, 42, 16, 14, 2, 3, 4, 2, 2, 1, 1, 1, 1])
            ]
        )
    ]
    t = Test(variants=variants)
    t.report()


if __name__ == '__main__':
    main()
