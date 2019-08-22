# abtest
A library for making resolution decisions on AB tests.

## Methodology

We use a Bayesian AB testing methodology inspired by [this white paper](https://cdn2.hubspot.net/hubfs/310840/VWO_SmartStats_technical_whitepaper.pdf). Compared to traditional hypothesis testing, this methodology has the advantage of allowing us to check our results continuously, instead of only after a fixed number of samples. Compared to [alternative continuous-monitoring methods](www.evanmiller.org/ab-testing/sequential.html), this methodology allows us to have more than two test legs, weight each leg differently, apply different prior beliefs pre-test, and test without specifying desired effect size. Together, this means we can test quickly and flexibly.
To understand this methodology in detail, the white paper is a good place to start. Put simply, we generate probability distributions for the expected value of each test leg based on our observations, sample repeatedly from those distributions, and compare these samples to see how often each leg wins.
More specifically, we resolve a test once the expected loss - how much lift we could be forgoing by choosing a given variant - is below some "threshold of caring". Colloquially, this test methodology is less concerned with the question "how likely is it that this leg is better?" and more with "will I give anything up if I choose this leg?".
Technically, for Bernoulli tests (i.e. where each trial has a binary, success-or-failure outcome), we generate a beta distribution for each leg based on our priors and observed data. Where we have variable values associated with success outcomes, we can choose to model the value per success as either an exponential, Pareto (i.e. power law), or normal distribution - you should look at the data to see what makes sense! - and set an [appropriate distribution](https://en.wikipedia.org/wiki/Conjugate_prior#Table_of_conjugate_distributions) based on the observed values and their frequencies, and multiply this by our beta distribution.

## Usage

### Checking Test Results
Edit `bayes.py`'s `main()` function with your test data, and then run `python bayes.py` to see information about your test, including whether it can be resolved. The `variants` list should have the format:
```python
variants = [
    Variant(
        'name_of_variant',
        [
            Distribution(args_for_distribution),
            ...
        ]
    ),
    ...
]
```
Where `Distribution` could be, e.g., `Bernoulli`. See each distribution class for required arugments.

#### Which Distribution?
If each trial in the test is a binary variable with either a success or failure outcome (e.g. form-fills per arrival), use `Bernoulli`.

If each trial has a non-binary result (e.g. impressions per arrival), examine the resulting data first and consider its distribution, then choose `Exponential`, `Pareto`, or `Normal` as appropriate. For these distributions, `values` is a list containing all result values observed, and `frequencies` is a list of the number of trials in which that value was observed (i.e. `frequences[2]` is the number of trials where `values[2]` was observed).

If each trial can be separated into a binary and non-binary component (e.g. value per arrival -> binary on form filles per arrival and non-binary on value per form fill), you can set the second argument of each `Variant` to be a list containing a `Bernoulli` distribution on the binary component and another distribution on the non-binary component.

### Simulating a Test
Use `simulate.py` to run this resolution methodology against a grid of control and treatment success rates to explore test accuracy. Update `SAMPLES_PER_TEST` to adjust how many times to run a test at each point on the grid (more will take longer but give more accurate results), and `control_rate` and `treatment_rate` ranges to adjust the grid coordinates over which to search. Currently, this only allows for simulation of simple `Bernoulli` tests.
