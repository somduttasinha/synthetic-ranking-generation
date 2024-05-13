# Research Question: How can we adapt the current method to simulate synthetic rankings to tailor it to RBO's properties

<!--toc:start-->

- [Research Question: How can we adapt the current method to simulate synthetic rankings to tailor it to RBO's properties](#research-question-how-can-we-adapt-the-current-method-to-simulate-synthetic-rankings-to-tailor-it-to-rbos-properties)
  - [Background](#background)
    - [What is RBO?](#what-is-rbo)
    - [How is RBO calculated?](#how-is-rbo-calculated)
      - [RBO$^w$](#rbow)
      - [RBO$^a$](#rboa)
      - [RBO$^b$](#rbob)
    - [On the treatment of ties (Use [2])](#on-the-treatment-of-ties-use-2)
    - [Applications of RBO](#applications-of-rbo)
  - [Sub-questions](#sub-questions)
    - [What is the current method to simulate rankings?](#what-is-the-current-method-to-simulate-rankings)
    - [Why do we need synthetic rankings?](#why-do-we-need-synthetic-rankings)
    - [What are the specific properties of RBO?](#what-are-the-specific-properties-of-rbo)
    - [If any, which (parametrisable) probability distributions define the properties of rankings?](#if-any-which-parametrisable-probability-distributions-define-the-properties-of-rankings)
  - [Essay Plan](#essay-plan)
  - [References](#references)
  <!--toc:end-->

## Background

### What is RBO?

- Rank-biased overlap is a measure of similarity between two rankings which can have the following properties [1]:
  - non-conjointness
  - top-weightnedness
  - monotonic with increasing depth of evaluation
- parametrizable
  - `p` : persistence parameter

### How is RBO calculated?

The original text [1] gives formulae to calculate the monotonically increasing RBO$^min$, monotonically RBO$^max$ and the extrapolated estimate RBO$^ext$

#### RBO$^w$

#### RBO$^a$

#### RBO$^b$

### On the treatment of ties (Use [2])

### Applications of RBO

- in Machine Learning
  - "quantification of differences between feature importance is crucial for assessing model trustworthiness" [4]

## Sub-questions

### What is the current method to simulate rankings?

In [2], Corsi and Urbano introduce two variants of RBO that handle ties in a non-trivial manner (in [1], Webber made a basic assumption that ties should be treated as
'sports' rankings where all elements of a tie group inherit the top ranking). To demonstrate the capabilities of the tie-aware variants, they simulated two rankings of the
same 1000 elements (conjoint) items. Ties were introduced at random in these rankings. See [3] for the source code

0. `simulate_rankings`: generates the requested rankings

   - makes calls to `simulate_scores` and `score2id`

1. `simulate_scores`: generates scores in the range [0, 1].
   - input parameters
     - `tau` : underlying kendall tau between the two rankings, a `tau` of 1 indicates identical rankings
     - `n` : length of the rankings
     - `frac_ties_x` and `frac_ties_y` : desired proportion of ties in the final rankings
     - `n_groups_x` and `n_groups_y` : number of tie groups in x and y
   - this is done by simulating a bivariate normal distribution to generate a vector of two-dimensional data points of length n.
     - it is assumed that a standard normal distribution is followed. $x$ and $y$ have a covariance of $r$
       where $r$ is the Pearson correlation between $x$ and $y$
       - $r$ is derived from the parameter $\tau$ through the following approximation: $r \approx sin(\frac{\pi}{2} * \tau)$

- the vector is then mapped to the domain [0, 1] using the cdf function
- call to `make_ties` to introduce ties into the ranking

2. `make_ties` : given a desired number of ties and tie groups, this method introduces ties to the given vector. Tie groups are created and shuffled (Dirichlet
   distribution to avoid uniform group sizes as uniform group sizes are not realistic)
   - input parameters
     - `x` : input rankings
     - `n_ties` : desired number of ties
     - `n_groups` : desired number of tie groups

### Why do we need synthetic rankings?

- Existing uses of synthetic rankings
  - In ML: [5] - "the problem here is that the data-holder wishes to find the best machine learning method to use for their task, but they do not wish to share their
    dataset with the many machine learning researchers that may be able to provide suitable methods." - in this example, a synthetic data set is notionally "good" if
    the performance of the ML model is good for both the actual dataset and the synthetic dataset
    - How applicable is this framework to ranking comparisons in IR?

### What are the specific properties of RBO?


### If any, which (parametrisable) probability distributions define the properties of rankings?


- Analysis of real data
  - IR, TREC data?
  - perform statistical tests on real rankings to see if there are any significant relationships
    - chi squared test to see if the presence of tie groups is independent to depth of evaluation
- What are the properties of actual rankings?
  - how to find and process long rankings?
- Presence of tie-groups?
- Relationship between location of tie groups and depth?
  - are there more ties the deeper you are?
- is there a relationship between the previous element being part of a tie group or not?
  - i.e. let $T_i \in \{0, 1\}$ signify that the $i^\text{th}$ element is part of a tie group
  - is $P(t_i = 1 | t_{i-1} = 1)$ different to $P(t_i = 1)$
- how can we use the input Kendall's $\tau$ to tailor the generate rankings' degree of conjointness?
- different prefix lengths? (not relevant for now)
- parametrise it to introduce top-weightedness? (agreements at the top)
- Once we have finished creating the new ranking generation algorithm, we can
  use various statistical tests such as the Kolmogorov-Smirnov Test to check if
  the distributions are the same

## Essay Plan

- Abstract
- Introduction
- Background/Related Work
  - RBO
  - synthetic data generation
    - remark that there is little to no literature on simulated ranking data
    - most literature focuses on generating synthetic data for ML models
- Methodology
    - ranking encoding. We need to represent ties in rankngs in an intuitive manner. Maybe we have a section exploring different options
- Experimental set-up
- Results
- Discussion

  - perhaps we can show that measures such as 'vanilla' Kendall's $\tau$ do not perform as well as RBO on my synthetic data set because it does not prioritise
    top weightedness
  - e.g. we can do something like

  ```R
  rankings <- simulate_rankings(conjoint=TRUE, top_weighted = TRUE) # top_weighted parameter focusses agreements toward the top of the rankings
  tau_score <- kendalltau(rankings)
  rbo_score <- rbo(rankings)
  ```

  somehow show that the `rbo_score` reflects better. e.g. relative to some pre-defined baseline RBO score, it is much higher than `tau_score` is to
  its pre-defined baseline. This will show that generating synthetic rankings that is tailored to RBO properties is good.

- Conclusion and Future Work

## References

- [1] Webber 2010, "A Similarity Measure for Indefinite Rankings"
- [2] Corsi and Urbano 2024, "The Treatment of Ties in Rank-Biased Overlap"
- [3] Corsi and Urbano 2024, [GitHub repository](https://github.com/julian-urbano/sigir2024-rbo)
- [4] Sarrica, Quattrone, Quattrone 2022, "Introducing the Rank-Biased Overlap as Similarity Measure for Feature Importance in Explainable Machine Learning:
  A Case Study on Parkinson’s Disease""
- [5] Jordon, Yoon, Van der Schaar 2018 "Measuring the quality of Synthetic data for use in competitions"
- [6] Figueira and Vaz 2022, "Survey on Synthetic Data Generation, Evaluation Methods and GANs"
  - "it must be plausible and follow the underlying distribution of the original data" (pg 1)
    - in this case, the "original data" is the data generated by the existing simulation
  - "Generative Adversarial Models"
  - Evaluation of the quality of synthetic data
    - "One may want to generate synthetic data to improve the performance of a machine learning (ML) model, while others may need synthetic data with novel patterns
      without worrying too much about the performance of the model"
    - Section 5
