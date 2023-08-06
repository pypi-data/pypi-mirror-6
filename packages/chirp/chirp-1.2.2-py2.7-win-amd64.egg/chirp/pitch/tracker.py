# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
pitch-tracking from time-frequency reassignment spectrograms

This is the main entry point and includes the cpitch script.

Copyright (C) 2011 Daniel Meliza <dan // meliza.org>
Created 2011-07-29
"""
import numpy as nx
import os
import libtfr
from chirp.pitch import template, particle, vitterbi
from chirp.common.plg import pitchtrace
from chirp.common.config import _configurable
from chirp.common.math import nandecibels

_scriptdoc = """
Usage: cpitch [-c <config.cfg>] [-m <mask.ebl>] <signal.wav>

Calculates pitch of <signal.wav>, with optional masking by
<mask.ebl>. Output is to stdout.  See documentation for
configuration file details. """

base_seed = 3653268


class tracker(_configurable):
    """
    This class is the front-end programming interface to the pitch
    tracker.  It will calculate pitch as a function of time from a
    variety of inputs, including spectrograms and signal waveforms.
    Options are set at initialization time (see options for default
    values) but some can be altered for each analysis.

    spectrogram parameters
    =======================
    nfft    - number of frequency points in the spectrogram
    shift   - number of samples to shift for each analysis frame
    winsize - analysis window size; controls frequency resolution (< nfft)
    tfr_order - number of analysis tapers to use
    tfr_tm    - time support of tapers (leave as default, generally)
    tfr_flock - frequency locking (decreasing this reduces scatter in frequency dim)
    tfr_tlock - time locking (reduces scatter in time dim)

    pitch template parameters
    =========================
    pitch_range - range of possible pitch hypotheses (in Hz or relative freq. units)
    freq_range  - range of frequencies to analyze  (in Hz or relative freq. units)
    lobes       - number of harmonic lobes in template
    lobe_decay  - exponential decay factor for harmonic lobes
    neg_ampl    - size of negative lobes in template
    neg_width   - width of negative lobes in template
    remask_likelihood - if True, remask the likelihood (really helps with pitch halving)

    particle filter parameters
    ==========================
    max_jump     - maximum amount pitch can change between frames
    particles    - number of particles
    pow_thresh   - exclude frames where total power is below this (in linear units)
    rwalk_scale  - in excluded frames, how much is pitch allowed to drift (std. dev)
    chains       - number of simulation chains to use
    btrace       - whether to use Vitterbi algorithm to backtrace best path
    min_loglike  - floor for log likelihood (not a very important parameter)
    """

    options = dict(nfft=512,
                   shift=30,
                   winsize=401,
                   tfr_order=5,
                   tfr_tm=6.0,
                   tfr_flock=0.01,
                   tfr_tlock=5,
                   freq_range=(0.01, 0.4),
                   pitch_range=(0.02, 0.25),
                   lobes=7,
                   lobe_decay=0.85,
                   neg_ampl=0.35,
                   neg_width=9,
                   remask_likelihood=True,
                   max_jump=80,
                   particles=500,
                   pow_thresh=1e4,
                   row_thresh=0.02,
                   rwalk_scale=2,
                   chains=5,
                   btrace=False,
                   min_loglike=-100)
    config_sections = ('spectrogram', 'cpitch')

    def __init__(self, configfile=None, samplerate=None, **kwargs):
        """
        Initialize the pitch tracker. Options are resolved in the
        following order:

        class.options, configfile, **kwargs

        If samplerate is supplied, and pitch/freq values are in
        absolute units, will rescale the values by the sampling rate.
        Otherwise the ranges need to be specified in relative units.
        """
        self.readconfig(configfile)
        self.options.update(kwargs)
        try:
            self.options['freq_range'] = hz2rel(self.options['freq_range'], samplerate)
            self.options['pitch_range'] = hz2rel(self.options['pitch_range'], samplerate)
        except TypeError:
            raise ValueError("A frequency value was specified in Hz: samplerate is required")
        self.template = template.harmonic(**self.options)

    def track(self, signal, mask=None, cout=None, raw=False, **kwargs):
        """
        Calculate the pitch from a spectrogram or signal waveform.  If
        the input is a spectrogram, it needs to be calculated on the
        same logarithmic frequency grid as the harmonic template.
        Waveforms are converted to spectrograms using the stored
        parameters for the template.

        mask: a logical array, nfreq by nframes.  Only used if
              'remask_likelihood' option is set.

        Selected options:
        particles    number of particles in filter
        chains       number of simulation chains
        rwalk_scale  random walk in frames where power is low
        btrace       do backwards filter to find MAP estimate?
        cout         output some status info to this stream (default stdout)
        pow_thresh   minimum power in a frame for it to be included

        Returns first good frame, power in each frame (linear), mean of particles,
                variance of particles, MAP estimate (or None). Frequency units are rel.
        """
        options = self.options.copy()
        options.update(kwargs)
        btrace = options.get('btrace', False)
        chains = options.get('chains', 1)

        if signal.ndim == 1:
            spec = self.matched_spectrogram(signal)
        elif signal.ndim == 2:
            spec = signal
        else:
            raise ValueError("Can't process arrays with more than 2 dimensions")

        specpow, spec, starttime = specprocess(spec, **options)
        like = self.template.xcorr(spec, **options)
        if options['remask_likelihood'] and mask is not None:
            # the pgrid is a subset of the fgrid, so we can use this
            # relationship to pull out the rows we need
            assert mask.shape[0] == spec.shape[0], "Mask must have same # rows as spectrogram"
            rows = (self.template.fgrid >= self.template.pgrid[0]) & \
                (self.template.fgrid <= self.template.pgrid[-1])
            like[~mask[rows, starttime:starttime + spec.shape[1]]] = 0

        proposal = template.frame_xcorr(spec, **options)

        pitch_mmse = nx.zeros((spec.shape[1], chains))
        pitch_var = nx.zeros((spec.shape[1], chains))
        f_mean = lambda x: self.template.pgrid[x]
        f_msq  = lambda x: self.template.pgrid[x] ** 2
        if btrace:
            pitch_map = []
        for chain in xrange(chains):
            # may be some use in multithreading here
            if cout: cout.write("+ Chain %d: forward particle filter\n" % chain)
            pfilt = particle.smc(like, proposal, **options)
            pfilt.initialize(nparticles=options['particles'], seed=base_seed + chain * 1000)
            pitch_mmse[0, chain] = pfilt.integrate(func=f_mean)
            pitch_var[0, chain] = pfilt.integrate(func=f_msq)

            for f, p, w in pfilt.iterate(rwalk_scale=options['rwalk_scale'], keep_history=btrace or raw):
                pitch_mmse[f, chain] = pfilt.integrate(func=f_mean)
                pitch_var[f, chain] = pfilt.integrate(func=f_msq)

            if raw:
                return nx.column_stack(pfilt.particle_history), pfilt.loglike, proposal

            if btrace:
                if cout: cout.write("+ Chain %d: reverse Vitterbi filter\n" % chain)
                particle_values = nx.column_stack(pfilt.particle_history)
                pitch_map.append(vitterbi.filter(particle_values, pfilt.loglike, proposal, **kwargs))

        if btrace:
            pitch_map = nx.take(self.template.pgrid, nx.column_stack(pitch_map))
        else:
            pitch_map = None

        pitch_var -= pitch_mmse ** 2
        return starttime, pitch_mmse, pitch_var, pitch_map, {'stim.pow': nandecibels(specpow)}

    def matched_spectrogram(self, signal, Fs):
        """
        Calculate a spectrogram of a signal using the same parameters
        as the template.  Returns spectrogram, time grid, and freq grid.
        """
        options = self.options
        spec = libtfr.tfr_spec(signal, options['nfft'], options['shift'], options['winsize'],
                               options['tfr_order'], options['tfr_tm'], options['tfr_flock'],
                               options['tfr_tlock'], fgrid=self.template.fgrid)
        return spec, libtfr.tgrid(spec, Fs, options['shift']), self.template.fgrid * Fs

    def spectrogram_options_str(self):
        out = """\
* Spectrogram Parameters:
** Window size = %(winsize)d
** FFT size = %(nfft)d
** Tapers = %(tfr_order)d
** Time support = %(tfr_tm)f
** Frequency locking = %(tfr_flock)f
** Time locking = %(tfr_tlock)f""" % self.options
        return out

    def particle_options_str(self):
        """ Print parameters that affect particle tracker """
        out = """\
* Particle filter parameters:
** Number of chains = %(chains)d
** Particles per chain = %(particles)d
** Random walk scale = %(rwalk_scale)f
** Backtrace pitch = %(btrace)s"""
        return out % self.options

    def template_options_str(self):
        """ Print parameters that affect template """
        out = """\
* Harmonic template parameters:
** Max pitch jump = %(max_jump)d
** Pitch power threshold = %(pow_thresh)f
** Number of lobes = %(lobes)d
** Lobe decay = %(lobe_decay)f
** Negative lobe amplitude = %(neg_ampl)f
** Negative lobe width = %(neg_width)f
** Remask likelihood = %(remask_likelihood)s
** Frequency range: %(freq_range)s (rel)""" % self.options
        out += "\n** Pitch range: (%.3f, %.3f) (rel)" % (self.template.pgrid[0], self.template.pgrid[-1])
        out += "\n** Candidate pitch count: %d" % self.template.pgrid.size
        return out


def specprocess(spec, pow_thresh=1e3, row_thresh=0.02, **kwargs):
    """
    Preprocess a spectrogram before running it through the pitch
    detector.  Currently this consists of eliminating frames at the
    beginning and end where the total power is less than pow_thresh,
    or the proportion of nonzero rows is less than row_thresh.

    Although inputs should be segmented carefully, this helps to deal
    with cases where the mask may be so small at the beginning or end
    that the spectrogram is essentially masked out.

    Returns reduced spectrogram, index of first column kept
    """
    psd = spec ** 2
    specpow = nx.sqrt(psd.sum(0))
    nrows = (psd > 0).sum(0)
    ind = (specpow > pow_thresh) & (nrows > (row_thresh * psd.shape[0]))
    ind = nx.nonzero(ind)[0]
    if ind.size < 2:
        raise ValueError("Spectrogram is entirely below power threshold")
    return specpow[ind[0]:ind[-1] + 1], spec[:, ind[0]:ind[-1] + 1], ind[0]


def hz2rel(freqs, samplerate):
    """
    Convert frequency values to relative units, if needed.  Inputs are
    considered to be Hz if they're greater than 1.0
    """
    fun = lambda x: float(x) / samplerate if x > 1.0 else x
    return tuple(fun(f) for f in freqs)


def cpitch(argv=None, cout=None, cerr=None, **kwargs):
    """ The script front-end """
    import sys
    from chirp.version import version
    if argv is None:
        argv = sys.argv[1:]
    if cout is None:
        cout = sys.stdout
    if cerr is None:
        cerr = sys.stderr

    import getopt
    from chirp.common.config import configoptions
    config = configoptions()

    maskfile = None

    opts, args = getopt.getopt(argv, 'hvc:m:')

    for o, a in opts:
        if o == '-h':
            print _scriptdoc
            return -1
        elif o == '-v':
            print "cpitch version %s" % version
            return -1
        elif o == '-c':
            if not os.path.exists(a):
                print >> cout, "ERROR: config file %s doesn't exist" % a
                return -1
            config.read(a)
        elif o == '-m':
            maskfile = a
    if len(args) < 1:
        print _scriptdoc
        return -1

    print >> cout, "* Program: cpitch"
    print >> cout, "** Version: %s" % version
    print >> cout, "* Input: %s" % args[0]

    from ewave import wavfile
    try:
        fp = wavfile(args[0])
    except IOError:
        print >> cerr, "No such file %s" % args[0]
        return -2
    except:
        print >> cerr, "Input file %s must be in WAV format" % args[0]
        return -2

    pcm = fp.read()
    samplerate = fp.sampling_rate / 1000.
    print >> cout, "** Samples:", pcm.size
    print >> cout, "** Samplerate: %.2f (kHz)" % samplerate

    pt = tracker(configfile=config, samplerate=samplerate * 1000, **kwargs)
    print >> cout, pt.spectrogram_options_str()
    print >> cout, pt.template_options_str()
    print >> cout, "* DLFT spectrogram:"
    spec, tgrid, fgrid = pt.matched_spectrogram(pcm, samplerate)
    print >> cout, "** Dimensions:", spec.shape

    print >> cout, pt.particle_options_str()

    if maskfile is not None and os.path.exists(maskfile):
        from chirp.common.geom import elementlist, masker
        print >> cout, "* Mask file:", maskfile
        elems = elementlist.read(maskfile)
        mask = masker(configfile=config, **kwargs)
        for startcol, mspec, imask in mask.split(spec, elems, tgrid, fgrid, cout=cout):
            try:
                startframe, pitch_mmse, pitch_var, pitch_map, stats = pt.track(mspec, cout=cout, mask=imask)
                stats['p.map'] = None if pitch_map is None else pitch_map * samplerate
                T = tgrid[startframe + startcol:startframe + startcol + pitch_mmse.shape[0]]
                # + tracker.options['winsize'] / (samplerate * 1000) ??
                ptrace = pitchtrace(T, pitch_mmse * samplerate, pitch_var * samplerate * samplerate,
                                    **stats)
                print >> cout, "*** Pitch calculations:"
                ptrace.write(cout)
            except ValueError, e:
                print >> cout, "*** Pitch calculation error: %s" % e
                continue

    else:
        print >> cout, "* No mask file; calculating pitch for entire signal"
        print >> cout, "** Element 0, interval (%.2f, %.2f)" % (tgrid[0], tgrid[-1])
        try:
            startframe, pitch_mmse, pitch_var, pitch_map, stats = pt.track(spec, cout=cout)
            stats['p.map'] = None if pitch_map is None else pitch_map * samplerate
            T = tgrid[startframe:startframe + pitch_mmse.shape[0]]
            ptrace = pitchtrace(T, pitch_mmse * samplerate, pitch_var * samplerate * samplerate,
                                **stats)
            print >> cout, "*** Pitch calculations:"
            ptrace.write(cout)
        except ValueError, e:
            print >> cout, "*** Pitch calculation error: %s" % e

    return 0

# Variables:
# End:
