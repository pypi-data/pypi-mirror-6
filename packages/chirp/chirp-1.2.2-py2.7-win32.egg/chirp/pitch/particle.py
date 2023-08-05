# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""A simple particle filter implementation

Much of the particle filter code is ported from SMCTC [1]

[1] Johansen A.M., "SMCTC: Sequential Monte Carlo in C++", J Stat Soft 30: 1--41 (2009).
    http://www.jstatsoft.org/v30/i06

Copyright (C) 2011 Daniel Meliza <dan // meliza.org>
Created 2011-07-29
"""
import numpy as nx


class smc(object):
    """
    Particle filter based on Sequential Monte Carlo algorithm.  This
    is very specialized for the pitch tracking algorithm, in that the
    state variable is a scalar integer (the index into the pitch
    grid), and the importance weighting and proposal densities are
    rather simple.
    """

    def __init__(self, likelihood, proposal, resample_threshold=0.5, min_loglike=-100, **kwargs):
        """
        Initialize the sampler.  The two main inputs are a likelihood
        array, which has a row for each pitch value, and a column for
        each time frame (N total).  The values are the likelihood
        of the pitch for each frame.  The proposal array is used to
        randomly jitter particles.  It should have at most N-1
        columns, each of which contains the PDF of the proposal
        function.  Values can increase or decrease; the middle row
        corresponds to the probability of no change, with positive and
        negative shifts above and below.

        The data may fail to give a clear indication of the likelihood
        or proposal functions if the signal power is low.  If the
        likelihood is poorly defined, set all the values in that
        column to the same value.  This will not affect the relative
        weights of the particles.  If the transition between frames is
        poorly defined, set all the values to zero or nan in that
        column.  This will produce a non-finite CDF, which is handled
        by simply moving the particles forward, possibly with the
        addition of some noise.
        """
        assert likelihood.shape[1] > proposal.shape[1], \
            "Likelihood array must have at least 1 more row than proposal array"
        self.resample_threshold = resample_threshold
        self.min_loglike = min_loglike

        self.loglike  = nx.log(nx.maximum(likelihood, nx.exp(min_loglike)))
        self.nvalues = likelihood.shape[0]
        self.cproposal = nx.cumsum(proposal, axis=0)
        self.cproposal /= nx.where(self.cproposal[-1] > 0, self.cproposal[-1], nx.nan)
        self.nframes = self.cproposal.shape[1]

    def initialize(self, nparticles, sampled=True, seed=3653268):
        """
        Initialize the sampler.  Initial values may be chosen from a
        uniform distribution (sampled=False) or by sampling from the
        likelihood for the first frame (sampled=True). The latter may
        introduce a bit of bias but avoids starting out with a really
        low ESS when the likelihood is very sparse.
        """
        nx.random.seed(seed)
        if sampled:
            csum = nx.cumsum(nx.exp(self.loglike[:, 0]))
            csum /= csum[-1]
            self.particles = sample_cdf(csum, nparticles)
            self.weights = nx.zeros(nparticles)
        else:
            self.particles = nx.random.randint(0, self.nvalues, nparticles)
            self.weights = self.loglike[self.particles, 0] - self.loglike[self.particles, 0].max()
        self.frame = 0
        self.particle_history = []

    def iterate(self, rwalk_scale=0.0, keep_history=False):
        """
        Iteration of the particle filter. This consists of three steps:
        1) sample from the proposal density and change particle values
        2) calculate new particle weights
        3) rescale and resample weights as necessary

        After each iteration the frame number and current particle and
        weight values are yielded. If there are no more frames
        StopIteration is raised.
        """
        while self.frame < self.nframes:
            if keep_history:
                self.particle_history.append(self.particles.copy())
            self.move_particles(rwalk_scale)
            self.update_weights()
            self.rescale_and_resample()
            self.frame += 1
            yield self.frame, self.particles, self.weights
        if keep_history:
            self.particle_history.append(self.particles.copy())
        raise StopIteration("End of proposal densities")

    def iterate_all(self, *args, **kwargs):
        """
        Iterate through all the remaining frames.
        """
        for g in self.iterate(*args, **kwargs):
            pass

    def move_particles(self, rwalk_scale=0.0):
        """
        Move particles using cumulative proposal density.  If the cdf
        is not finite, then the particles are moved forward using a
        random walk.
        """
        np = self.particles.size
        cdf = self.cproposal[:, self.frame]
        if not nx.isfinite(cdf.sum()):
            if rwalk_scale > 0:
                self.particles += nx.round(nx.random.normal(scale=rwalk_scale, size=np)).astype(self.particles.dtype)
        else:
            self.particles += sample_cdf(self.cproposal[:, self.frame], np) - self.cproposal.shape[0] / 2

    def update_weights(self):
        """
        Update weights for current frame using currently set particle
        values. Invalid values get severely penalized (min_loglike).
        """
        valid = (self.particles >= 0) & (self.particles < self.nvalues)
        self.weights[valid] += self.loglike[self.particles[valid], self.frame + 1]
        self.weights[~valid] += self.min_loglike

    def rescale_and_resample(self):
        """
        1. Rescale weights so that the max (log) weight is 0
        2. Check if ESS is below threshold
        3. Resample if below threshold
        """
        np = self.particles.size
        max_weight = self.weights.max()
        self.weights -= max_weight
        if self.ess() < (self.resample_threshold * np):
            # this uses the same algorithm as SMC_RESAMPLE_RESIDUAL
            # if a particle has a weight greater than 1/N, it's replicated that many times
            # the remaining unused particles are sampled from the residual probabilities
            rsweights = nx.exp(self.weights)
            rsweights *= np / rsweights.sum()
            counts = nx.floor(rsweights).astype('i')
            rsweights -= counts
            residcount = np - nx.sum(counts)
            counts += nx.random.multinomial(residcount, rsweights / rsweights.sum())

            # then replicate chosen particles
            self.particles = nx.repeat(self.particles, counts)
            # weights are equalized (because distribution of particles now reflects weights)
            self.weights[:] = 0   # nx.log(1./np)

    def ess(self):
        """
        Calculate effective sample size
        """
        s1 = nx.exp(self.weights).sum()
        s2 = nx.exp(2 * self.weights).sum()
        return nx.exp(2 * nx.log(s1) - nx.log(s2))

    def density(self, particles=None, weights=None):
        """
        Estimate density from particles.  This is essentially an
        accumulated sum of the weights for each bin.
        """
        from itertools import izip
        if particles is None: particles = self.particles
        if weights is None: weights = nx.exp(self.weights)
        pdf = nx.zeros(self.nvalues)
        wsum = 0.0
        for p, w in izip(particles, weights):
            if p < 0 or p >= self.nvalues: continue
            wsum += w
            pdf[p] += w
        return pdf / wsum

    def integrate(self, particles=None, weights=None, func=None):
        """
        Evaluate an integrand over the distribution. Default is a
        weighted sum.
        """
        if particles is None: particles = self.particles
        if weights is None: weights = nx.exp(self.weights)
        ind = (particles >= 0) & (particles < self.nvalues)
        if func is None:
            wsum = nx.sum(particles[ind] * weights[ind])
        else:
            wsum = nx.sum(func(particles[ind]) * weights[ind])
        return wsum / nx.sum(weights[ind])


def sample_cdf(cdf, N):
    """
    Sample N values from cdf using U_{0, 1} trick
    """
    u01 = nx.random.uniform(size=N)
    return nx.searchsorted(cdf, u01)


# Variables:
# End:
