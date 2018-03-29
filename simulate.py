#!/usr/bin/env python

import random
import statistics as stats

import bayes
import simulation


SAMPLES_PER_TEST = 100


def run_simulation(test, check_every=500):

    method = bayes.Test(verbose=False)

    while not method.done:
        test.trial()
        
        if test.trials % check_every == 0:

            # TODO (db): extend this to support other distributions
            method.variants = [
                bayes.Variant(
                    l.name, [bayes.Bernoulli(1, 1, l.trials, l.successes)]
                )
                for l in test.legs
            ]

            method.report()    

    return method


def run_test(control_rate, treatment_rate):

    tests = 0
    trial_counts = []
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0
    true_nulls = 0
    false_nulls = 0

    for i in range(SAMPLES_PER_TEST):

        control = simulation.Leg('control', 0.5, control_rate)
        treatment = simulation.Leg('treatment', 0.5, treatment_rate)
        test = simulation.ABTest(control, treatment)

        results = run_simulation(test)

        tests += 1
        trial_counts.append(test.trials)

        if treatment.rate > control.rate:
            if results.winner == 'treatment':
                true_positives += 1
            elif results.winner == 'control':
                false_negatives += 1
            else:
                false_nulls += 1

        elif treatment.rate < control.rate:
            if results.winner == 'treatment':
                false_positives += 1
            elif results.winner == 'control':
                true_negatives += 1
            else:
                false_nulls += 1

        elif treatment.rate == control.rate:
            if results.winner == 'treatment':
                false_positives += 1
            elif results.winner == 'control':
                false_negatives += 1
            else:
                true_nulls += 1

    return (
        control_rate,
        treatment_rate,
        stats.mean(trial_counts),
        stats.median(trial_counts),
        float(true_positives) / tests,
        float(false_positives) / tests,
        float(true_negatives) / tests,
        float(false_negatives) / tests,
        float(true_nulls) / tests,
        float(false_nulls) / tests
    )


def main():

    results = []

    # establish output headers
    results.append((
        'control_rate',
        'treatment_rate',
        'mean_trials',
        'median_trials',
        'true_positive',
        'false_positive',
        'true_negative',
        'false_negative',
        'true_null',
        'false_null'
    ))

    for control_rate in range(1, 50):
        for treatment_rate in range(1, 50):
            results.append(run_test(control_rate * 0.01, treatment_rate * 0.01))

    with open('out.csv', 'w') as outf:
        for result in results:
            print(result)
            outf.write(','.join(str(i) for i in result))
            outf.write('\n')


if __name__ == '__main__':
    main()
