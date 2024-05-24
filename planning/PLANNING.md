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

The original text [1] gives formulae to calculate the monotonically increasing
RBO$^\text{min}$, monotonically RBO$^\text{max}$ and the extrapolated estimate RBO$^\text{ext}$

#### RBO$^w$

#### RBO$^a$

#### RBO$^b$

### On the treatment of ties (Use [2])

### Applications of RBO

- in Machine Learning
  - "quantification of differences between feature importance is crucial for assessing model trustworthiness" [4]

## Sub-questions

### What is the current method to simulate rankings?

In [2], Corsi and Urbano introduce two variants of RBO that handle ties in a
non-trivial manner (in [1], Webber made a basic assumption that ties should be
treated as 'sports' rankings where all elements of a tie group inherit the top
ranking). To demonstrate the capabilities of the tie-aware variants, they
simulated two rankings of the same 1000 elements (conjoint) items. Ties were
introduced at random in these rankings. See [3] for the source code. This will
have fully conjoint domains which is not the case with RBO calculations.

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
  - In ML: [5] - "the problem here is that the data-holder wishes to find the
    best machine learning method to use for their task, but they do not wish to
    share their dataset with the many machine learning researchers that may be
    able to provide suitable methods." - in this example, a synthetic data set
    is notionally "good" if the performance of the ML model is good for both the
    actual dataset and the synthetic dataset
    - How applicable is this framework to ranking comparisons in IR?

### What are the specific properties of RBO?

### If any, which (parametrisable) probability distributions define the properties of rankings?

#### Conjointness of the domains

- Let $A$ and $B$ be the domains from which the rankings $S$ and $L$ are drawn
  respectiveley
- The user gives some chosen Jaccard Similarity value as input, as well as the
  desired sizes of both domains $|A| = a$ and $|B| = b$
- Jaccard Similarity is calculated as:
  - $J(A, B) = \frac{|A \cap B|}{|A \cup B|}$
  - $|A \cup B| = a + b - |A \cap B|$
  - $J(A, B) (a + b - |A \cap B|) = |A \cap B|$
  - $J(A, B) (a + b) - J(A, B)(|A \cap B|) = |A \cap B|$
  - $J(A, B) (a + b) = J(A, B)(|A \cap B|) + |A \cap B|$
  - $|A \cap B| = \frac{J(A, B) (a + b)}{1 + J(A, B)}$
- From these derivations, we can find the size of the intersection. To ensure
  that this is an integer, we use the floor of the last term as the size of
  the intersection. Let this value be $p$.
- We generate $p$ items and add them to both $A$ and $B$.
- We then add $a - p$ uniquely labelled elements to $A$
- Finally, we add $b - p$ uniquely labelled elements to $B$

#### Top weightedness

- Formalisms

  - Let the two domains be $A$ and $B$. The sizes of both sets are $a$ and $b$ respectively

- Overlap at depth k

  - 3 ways to increase overlap:
    - 1. sample from the set $(A - S) \cap L$, add item to $S$
    - 2. sample from the set $S \cap (B - L)$, add item to $L$
    - 4. sample from the set $A \cap B$, add item to both $S$ and $L$
  - if we choose to increase overlap, we choose one of these cases with equal probability
  - we will parametrise this by some top-weightedness coefficient $\theta$
  - if $\theta = 0$, the prob of agreement should follow a $U(0, n)$ distribution
    where $n = \text{min}(a, b)$
  - if $\theta = 1$, the prob of agreement should follow some sort of bounded $\text{exp}(1)$ distribution
  - $\theta$ describes the degree of top-weightedness
  - for a high value of $\theta$, we would like some sort of decaying function
    such that at earlier depths, the probability of agreement
    is higher than at later depths. For a low value of $\theta$, we do not need
  - we have the general function: $f(x) = \theta (e^{-\frac{x}{k}}) + (1 - \theta)(\frac{1}{n})$
    - $\theta$ : top-weightedness
    - $k$ : some function of the size of the domain. This ensure that the
      decaying is scaled to the size of the domain. For example, we can say that
      for $\theta = 1$, we want the probability of increasing overlap to be greater
      than completely random for the first 30% of items ranked. Then:
      - $e^{\frac{-0.3n}{k}} = \frac{1}{n}$
      - solving for $k$, we find that $k = \frac{0.3n}{ln(n)}$

#### Ties

- Relationship between location of tie groups and depth?
  - are there more ties the deeper you are?
- is there a relationship between the previous element being part of a tie group
  or not?

  - i.e. let $T_i \in \{0, 1\}$ signify that the $i^\text{th}$ element is part
    of a tie group
  - is $P(t_i = 1 | t_{i-1} = 1)$ different to $P(t_i = 1)$

- Input:
  - `frac_ties_x`, `frac_ties_y`
  - `num_groups_x`, `num_groups_y`

## Final Algorithm

### Pseudocode

(TODO)

## Essay Plan

- Abstract
- Introduction
  - Broad statement regarding the importance of ranking systems in general in
    various applications
    - Ranking systems are ubiquitous across several domains, ranging from
      university rankings [7] to information retrieval [8] and recommender systems
      [9]. They are used to organise and present information in an
      easy-to-understand manner. Designing effective ranking systems may involve
      comparing different rankings using some objective manner. In [1], the authors
      describe a hypothetical scenario where a researcher wishes to improve the
      efficiency of an existing IR system by _query pruning_. To measure the
      accuracy of this new system taking the original system as a reference, there
      is a need for a similarity measure.
  - Problem statement:
    - current state of research
      - in [2], the authors introduce two variants of RBO to handle ties. To
        demonstrate the relative efficacy of the two techniques, the authors use
        both TREC data and synthetic data. To demonstrate the advantages
        of RBO as a rank-similarity measure over other measures, the synthetic
        data should be geared toward's RBO's unique properties of non-conjointness,
        top-weightedness and indefiniteness [1].
      - The method of simulating data is not entirely suited to RBO's properties
        because it does not simulate data from non-conjoint rankings.
      -
    - gap in research as of now
      - perhaps show that executing a query of "RBO synthetic data
        generation" on various literature search engines yield very
        few results thus demonstrating that my contribution is
        necessary
  - objective of the study
  - significance of the study
  - outline of the paper
- Background/Related Work
  - introduction to rankings systems
  - introduction to RBO
  - synthetic data generation
    - remark that there is little to no literature on simulated ranking data
    - most literature focuses on generating synthetic data for ML models
- Methodology
  - ranking encoding. We need to represent ties in rankngs in an intuitive manner.
    Maybe we have a section exploring different options
- Experimental set-up
- Results
- Discussion

  - perhaps we can show that measures such as Kendall's $\tau$ do not perform as
    well as RBO on my synthetic data set because it does not prioritise
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
- [7] Rafique, Awan, Shafiq, Mahmood, 2023, "Exploring the role of ranking
  systems towards university performance improvement: A focus group-based study"
- [8] Page, Brin, Motwani, Winograd et al, 1999, "The pagerank citation ranking:
  Bringing order to the web"
- [9] Karatzoglou, Baltrunas and Shi, 2013, "Learning to Rank for Recommender Systems"
