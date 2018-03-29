# abtest
A library for making resolution decisions on AB tests. More methodology information available [here](https://git.cogolo.net/uplift/uplift/wiki/AB-Testing).

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
