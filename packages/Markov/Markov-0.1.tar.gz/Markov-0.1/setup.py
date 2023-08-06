from distutils.core import setup

setup(name='Markov',
      version='0.1',
      description='Python library for Hidden Markov Models',
      author='Dr Peter J Bleackley',
      author_email='pete.bleackley@btinternet.com',
      url='http://code.google.com/p/python-hidden-markov/',
      download_url='https://drive.google.com/#folders/0B68FS-e9xvMYYlhaNnluLXpFRlE',
      py_modules=['Markov'],
      classifiers=["Programming Language :: Python",
                   "Programming Language :: Python :: 2.7",
                   "Development Status :: 3 - Alpha",
                   "Environment :: Other Environment",
                   "Intended Audience :: Science/Research",
                   "Intended Audience :: Information Technology",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)",
                   "Operating System :: OS Independent",
                   "Topic :: Scientific/Engineering :: Artificial Intelligence",
                   "Topic :: Software Development :: Libraries",
                   "Topic :: Software Development :: Libraries :: Python Modules"],
      long_description="""
                       ==================================
                       Python Hidden Markov Model Library
                       ==================================

                       This library is a pure Python implementation of Hidden
                       Markov Models (HMMs). The project structure is quite
                       simple::

                       Help on module Markov:

                       NAME
                           Markov - Library to implement hidden Markov Models

                       FILE
                           Markov.py

                       CLASSES
                            __builtin__.object
                                BayesianModel
                                    HMM
                                Distribution
                                    PoissonDistribution
                                Probability
    
                       class BayesianModel(__builtin__.object)
                        |  Represents a Bayesian probability model
                        |  
                        |  Methods defined here:
                        |  
                        |  MaximumLikelihoodOutcome(self, PriorProbs=None)
                        |      Returns the maximum likelihood outcome given PriorProbs
                        |  
                        |  MaximumLikelihoodState(self, Observations=None)
                        |      Returns the maximum likelihood of the internal state. If Observations
                        |      is None, defaults to the maximum likelihood of the Prior
                        |  
                        |  Outcomes(self)
                        |      Returns an iterator over the possible outcomes
                        |  
                        |  PriorProbs(self, Observations, PriorDist=None)
                        |      Returns a Distribution representing the probabilities of the prior
                        |      states, given a probability Distribution of Observations
                        |  
                        |  States(self)
                        |      Returns an iterator over the possible states
                        |  
                        |  __call__(self, PriorProbs=None)
                        |      Returns a Distribution representing the probabilities of the outcomes
                        |      given a particular distribution of the priors, which defaults to
                        |      self.Prior
                        |  
                        |  __iadd__(self, Model2)
                        |      Updates the BayesianModel with the data in another BayesianModel
                        |  
                        |  __init__(self, Prior, Conditionals)
                        |      Prior is a Distribution. Conditionals is a dictionary mapping
                        |      each state in Prior to a Distribution
                        |  
                        |  ----------------------------------------------------------------------
                        |  Data descriptors defined here:
                        |  
                        |  __dict__
                        |      dictionary for instance variables (if defined)
                        |  
                        |  __weakref__
                        |      list of weak references to the object (if defined)
    
                       class Distribution(__builtin__.object)
                        |  Represents a probability distribution over a set of categories
                        |  
                        |  Methods defined here:
                        |  
                        |  MaximumLikelihoodState(self)
                        |      Returns the state with the greatest likelihood
                        |  
                        |  Sample(self)
                        |      Picks a random sample from the distribution
                        |  
                        |  States(self)
                        |      Yields the Distribution's states
                        |  
                        |  Update(self, categories)
                        |      Updates each category in the probability distiribution, according to
                        |      a dictionary of numerator and denominator values
                        |  
                        |  __call__(self, item)
                        |      Gives the probability of item
                        |  
                        |  __iadd__(self, Dist2)
                        |      Updates the Distribution given another Distribution with the same states
                        |  
                        |  __init__(self, categories, k=0)
                        |      The distribution may be initialised from a list of categories or a
                        |      dictionary of category frequencies. In the latter case, Laplacian
                        |      smoothing may be used
                        |  
                        |  __mul__(self, scalar)
                        |      Returns the probability of each item, multiplied by a scalar
                        |  
                        |  copy(self)
                        |      Returns a copy of the Distribution
                        |  
                        |  ----------------------------------------------------------------------
                        |  Data descriptors defined here:
                        |  
                        |  __dict__
                        |      dictionary for instance variables (if defined)
                        |  
                        |  __weakref__
                        |      list of weak references to the object (if defined)
    
                       class HMM(BayesianModel)
                        |  Represents a Hidden Markov Model
                        |  
                        |  Method resolution order:
                        |      HMM
                        |      BayesianModel
                        |      __builtin__.object
                        |  
                        |  Methods defined here:
                        |  
                        |  Analyse(self, Sequence, MaximumLikelihood=False)
                        |      Yields the an estimate of the internal states that generated a Sequence
                        |      of observed values, either as the Maximum Likelihood state
                        |      (Maximumlikelihood=True) or as a Distribution (MaximumLikelihood=False)
                        |  
                        |  MaximumLikelihoodState(self, Observations=None)
                        |      Returns the maximum likelihood of the internal state. If Observations
                        |      is None, defaults to the maximum likelihood of the the Current state, or
                        |      the Prior if self.Current is None
                        |  
                        |  Outcomes(self)
                        |  
                        |  Predict(self)
                        |      Returns a Distribution representing the probabilities of the next
                        |      state given the current state
                        |  
                        |  PriorProbs(self, Observations)
                        |      Returns a Distribution the prior probabilities of the HMM's states
                        |      given a Distribution of Observations
                        |  
                        |  Train(self, Sequence)
                        |      Trains the HMM from a sequence of observations
                        |  
                        |  Update(self, Observations)
                        |      Updates the Prior probabilities, TransitionProbs
                        |      and Conditionals given Observations
                        |  
                        |  __call__(self, PriorProbs=None)
                        |      Returns a Distribution of outcomes given PriorProbs, which defaults
                        |      to self.Current if it is set, or self.Prior otherwise
                        |  
                        |  __init__(self, states, outcomes)
                        |      states is a list or dictionary of states, outcomes is a dictionary
                        |      mapping each state in states to a Distribution of the output states
                        |  
                        |  ----------------------------------------------------------------------
                        |  Methods inherited from BayesianModel:
                        |  
                        |  MaximumLikelihoodOutcome(self, PriorProbs=None)
                        |      Returns the maximum likelihood outcome given PriorProbs
                        |  
                        |  States(self)
                        |      Returns an iterator over the possible states
                        |  
                        |  __iadd__(self, Model2)
                        |      Updates the BayesianModel with the data in another BayesianModel
                        |  
                        |  ----------------------------------------------------------------------
                        |  Data descriptors inherited from BayesianModel:
                        |  
                        |  __dict__
                        |      dictionary for instance variables (if defined)
                        |  
                        |  __weakref__
                        |      list of weak references to the object (if defined)
    
                       class PoissonDistribution(Distribution)
                        |  Represents a Poisson distribution
                        |  
                        |  Method resolution order:
                        |      PoissonDistribution
                        |      Distribution
                        |      __builtin__.object
                        |  
                        |  Methods defined here:
                        |  
                        |  MaximumLikelihoodState(self)
                        |  
                        |  Mean(self)
                        |      Returns the Mean of the PoissonDistribution
                        |  
                        |  Sample(self)
                        |      Returns a random sample from the Poisson distribution
                        |  
                        |  States(self, limit=1e-07)
                        |      Yields the PoissonDistribution's states, up to a cumulative
                        |      probability of 1-limit
                        |  
                        |  Update(self, N, p=1.0)
                        |      Updates the distribution, given a value N that has a probability of P
                        |      of being drawn from this distribution
                        |  
                        |  __call__(self, N)
                        |      Returns the probability of N
                        |  
                        |  __init__(self, mean)
                        |      Initialises the distribution with a given mean
                        |  
                        |  copy(self)
                        |      Returns a copy of the PoissonDistribution
                        |  
                        |  ----------------------------------------------------------------------
                        |  Methods inherited from Distribution:
                        |  
                        |  __iadd__(self, Dist2)
                        |      Updates the Distribution given another Distribution with the same states
                        |  
                        |  __mul__(self, scalar)
                        |      Returns the probability of each item, multiplied by a scalar
                        |  
                        |  ----------------------------------------------------------------------
                        |  Data descriptors inherited from Distribution:
                        |  
                        |  __dict__
                        |      dictionary for instance variables (if defined)
                        |  
                        |  __weakref__
                        |      list of weak references to the object (if defined)
    
                       class Probability(__builtin__.object)
                        |  Represents a probability as a callable object
                        |  
                        |  Methods defined here:
                        |  
                        |  Update(self, deltaN, deltaD)
                        |      Updates the probability during Bayesian learning
                        |  
                        |  __call__(self)
                        |      Returns the value of the probability
                        |  
                        |  __iadd__(self, Prob2)
                        |      Updates the probability given another Probability object
                        |  
                        |  __init__(self, n, d)
                        |      Initialises the probability from a numerator and a denominator
                        |  
                        |  ----------------------------------------------------------------------
                        |  Data descriptors defined here:
                        |  
                        |  __dict__
                        |      dictionary for instance variables (if defined)
                        |  
                        |  __weakref__
                        |      list of weak references to the object (if defined)
                """

      )
