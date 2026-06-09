# alopecia_simulations
(DA) Sample size estimations for induced alopecia project using a biologically structured stochastic disease progression simulator + mixed-model power engine.

There are essentially two versions of the same model here, `simulate_power.py` and `batch_simulate.py` which work on standalone or multi-core systems (the latter through a `SLURM` job submission system (or equivalent, although example `sbatch` script is provided here if `SLURM` is your system of choice).

**Npte**. This is far from a *perfect* solution, but rather a series of assumptions, approximations (and probably some terrible oversights). Please take a look at the **Assumptions**, **Logic** and **Limitations** sections below and interpret any results with an appropriate amount of caution.

## Prerequisites

```python
numpy
pandas
json
statsmodels
matplotlib
```

## Assumptions

* Penetrance is fixed and independent
  - Each animal has an 83% probability of responding to the injection.
  - Whether an individual responds is independent of all other individuals and of treatment assignment.
* Non-penetrant individuals have zero phenotype
  - Individuals that do not respond to injection are assigned 0% hair loss at both timepoints.
  - There is no partial or intermediate response class.
* Penetrant individuals follow the observed pilot data distribution (which is limited).
  - Week 8 hair loss is drawn from a normal distribution fitted to the pilot penetrant data.
  -Week 12 hair loss is generated as Week 8 plus a progression term.
* Disease progression is additive and non-negative
  - Week 12 = Week 8 + progression.
  - Progression is drawn from a normal distribution estimated from pilot data differences.
  - Progression is truncated so it cannot be negative.
* Hair loss is bounded between 0 and 100
  - Values below 0 are set to 0.
  - Values above 100 are set to 100.
* Correlation between timepoints is fully explained by progression
  - There is no independent noise at Week 12 beyond progression.
* Treatment acts multiplicatively on phenotype
  - Treatment reduces both Week 8 and Week 12 values by a fixed proportion (not a perfect solution).
  - The effect is instantaneous and identical at both timepoints (not a perfect solution).
  - Treatment does not alter penetrance.
* Treatment does not change variability structure
  - The variance of responses is assumed unchanged under treatment, only scaled.
* Mixed-effects model is correctly specified
  - Hair loss depends linearly on group and time.
  - Individual ID is a random intercept capturing repeated measures correlation.
  - No interaction between treatment and time is included in the primary test.
* Statistical inference is based on asymptotic p-values
  - Significance is determined using Wald tests from the fitted mixed model.
  - These p-values are assumed reliable at all sample sizes explored.


## Logic of the simulation


* Define biological variability from pilot data
  - Estimate mean and variance of Week 8 severity.
  - Estimate mean and variance of progression from Week 8 to Week 12.
* Generate synthetic individuals
  - Each individual is assigned a penetrance outcome.
  - If penetrant, assign a severity trajectory (Week 8 + progression).
  - If not penetrant, assign zero phenotype.
* Assign treatment groups
  - Control individuals follow the baseline generative process.
  - Treated individuals have their phenotype scaled down.
* Construct longitudinal dataset
  - Each individual contributes two observations (Week 8 and Week 12).
* Fit mixed-effects model
  - Outcome: hair loss
  - Fixed effects: treatment group and time
   -Random effect: individual ID
* Test for treatment effect
  - Extract p-value for treatment term.
* Repeat experiment many times
  - Estimate probability that p < 0.05 for each sample size and effect size.
* Derive power curves and sample size thresholds
  - Identify minimum N per group achieving 80% and 90% power.
* Repeat across penetrance values
  - Evaluate sensitivity of required sample size to induction efficiency.


## Limitations

* Extremely small pilot dataset
  - The entire distributional structure is estimated from only 5 penetrant individuals.
  - This makes variance and progression estimates unstable and highly uncertain.
* Distributional assumptions are arbitrary
  - Normal distributions are assumed for both severity and progression.
  - Hair loss data are bounded and likely non-normal in reality.
* Penetrance is overly simplified
  - Treated as binary.
  - Real systems often have partial responders or graded induction.
* Independence assumptions may be violated
  - Individuals may share batch effects or experimental clustering not modeled here.
* Treatment mechanism is oversimplified
  - The model assumes uniform proportional reduction.
* No explicit treatment × time interaction in inference
  - The model tests a main effect of group rather than a mechanistic longitudinal effect.
  - This may reduce sensitivity or misalign with biological hypotheses.
* Progression is forced to be monotonic
  - Real biological systems may show regression or plateau effects.
* Mixed model assumptions may not hold
  - Residuals are unlikely to be normally distributed.
  - Variance may differ between groups or timepoints.
  - Small sample sizes may violate asymptotic assumptions for p-values.
* Power estimates are conditional on model correctness
  - Results are only valid if the assumed generative model matches reality.
  - Any mismatch in penetrance, variance, or treatment mechanism will bias sample size estimates.
