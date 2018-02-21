#!/usr/bin/env python

import math


class Method:
    
    def check(self):
        raise NotImplementedError


class TwoSidedSequentialSampling(Method):

    alpha = 0.05
    power = 0.8
    effect_size = 0.1

    # these are fixed for params above
    max_successes = 3250
    max_lead = 2.24 * math.sqrt(max_successes)

    def __init__(self, base_rate):
        self.base_rate = base_rate
        self.done = False

    def is_valid_abtest(self):
        if len(self.abtest.legs) > 2:
            raise TypeError('AB Test should have two legs')

        if 'control' not in self.abtest.legs:
            raise TypeError('AB Test should have control leg')

        if 'treatment' not in self.abtest.legs:
            raise TypeError('AB Test should have treatment leg')

    def check(self):

        if self.done:
            return

        self.abtest.trial()

        if self.abtest.successes >= self.max_successes:
            self.done = True
            self.winner = None

        if (self.abtest.legs['treatment'].successes
                - self.abtest.legs['control'].successes
                >= self.max_lead):
            self.done = True
            self.winner = 'treatment'

        if (self.abtest.legs['control'].successes
                - self.abtest.legs['treatment'].successes
                >= self.max_lead):
            self.done = True
            self.winner = 'control'

    def run(self, abtest):
        self.abtest = abtest
        self.is_valid_abtest()

        while not self.done:
            self.abtest.trial()
            self.check()
