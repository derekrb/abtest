#!/usr/bin/env python

import math
import random


class Leg:

    def __init__(self, name, weight, rate):
        self.name = name
        self.rate = rate
        self.weight = weight
        self.trials = 0
        self.successes = 0

    def trial(self):
        result = int(random.random() < self.rate)
        self.trials += 1
        self.successes += result
        return result


class ABTest:

    def __init__(self, *legs):
        self.legs = list(legs)
        self.trials = 0
        self.successes = 0

    def pick_leg(self):
        legs_scored = [(math.pow(random.random(), 1 / float(l.weight)), l)
                        for l in self.legs]
        return max(legs_scored)[1]

    def trial(self):
        leg = self.pick_leg()
        result = leg.trial()
        self.trials += 1
        self.successes += result
