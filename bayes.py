#!/usr/bin/env python

'''
inspired by: https://cdn2.hubspot.net/hubfs/310840/VWO_SmartStats_technical_whitepaper.pdf
'''

import numpy as np

import abtest


class Variant:

    def __init__(self, name, a, b, n, c):
        self.name = name
        self.a = a
        self.b = b
        self.n = n
        self.c = c

    def sample_posterior(self, n_samples):
        self.samples = (np.random.beta(
            self.a + self.c, self.b + self.n - self.c,
            size=n_samples
        ))


class Test:

    def __init__(self, variants=None, **kwargs):
        # note: variant[0] is taken to be control!
        if variants:
            self.variants = [Variant(*i) for i in variants]
        else:
            self.variants = []
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
        for i, variant in enumerate(self.variants):

            variant.beats_control = np.sum(
                np.greater(
                    variant.samples,
                    self.variants[0].samples
                )
            ) / self.n_samples
            variant.beats_all = np.sum(
                np.equal(
                    variant.samples,
                    np.amax(self.samples, axis=0)
                )
            ) / self.n_samples
            variant.loss = np.sum(
                np.amax(
                    self.samples - np.tile(
                        variant.samples, (len(self.variants), 1)
                    ),
                    axis=0
                )
            ) / self.n_samples

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
        ('control', 1, 1, 30, 16),
        ('treatment', 1, 1, 41, 11),
    ]
    t = Test(variants=variants)
    t.report()


if __name__ == '__main__':
    main()
