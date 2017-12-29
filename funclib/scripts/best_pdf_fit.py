#pylint: skip-file
'''this is the doc string'''

import warnings as _warnings
import numpy as _np
import pandas as _pd
import scipy.stats as _st
import statsmodels as _sm
import matplotlib as _mpl
import matplotlib.pyplot as plt

matplotlib.rcParams['figure.figsize'] = (16.0, 12.0)
matplotlib.style.use('ggplot')

# Create models from data
def best_fit_distribution(data, bins=200, ax=None):
    """Model data by finding best fit distribution to data"""
    # Get histogram of original data
    y, x = _np.histogram(data, bins=bins, normed=True)
    x = (x + _np.roll(x, -1))[:-1] / 2.0

    # Distributions to check
    DISTRIBUTIONS = [        
        _st.alpha, _st.anglit, _st.arcsine, _st.beta, _st.betaprime, _st.bradford, _st.burr, _st.cauchy, _st.chi, _st.chi2, _st.cosine,
        _st.dgamma, _st.dweibull, _st.erlang, _st.expon, _st.exponnorm, _st.exponweib, _st.exponpow, _st.f, _st.fatiguelife, _st.fisk,
        _st.foldcauchy, _st.foldnorm, _st.frechet_r, _st.frechet_l, _st.genlogistic, _st.genpareto, _st.gennorm, _st.genexpon,
        _st.genextreme, _st.gausshyper, _st.gamma, _st.gengamma, _st.genhalflogistic, _st.gilbrat, _st.gompertz, _st.gumbel_r,
        _st.gumbel_l, _st.halfcauchy, _st.halflogistic, _st.halfnorm, _st.halfgennorm, _st.hypsecant, _st.invgamma, _st.invgauss,
        _st.invweibull, _st.johnsonsb, _st.johnsonsu, _st.ksone, _st.kstwobign, _st.laplace, _st.levy, _st.levy_l, _st.levy_stable,
        _st.logistic, _st.loggamma, _st.loglaplace, _st.lognorm, _st.lomax, _st.maxwell, _st.mielke, _st.nakagami, _st.ncx2, _st.ncf,
        _st.nct, _st.norm, _st.pareto, _st.pearson3, _st.powerlaw, _st.powerlognorm, _st.powernorm, _st.rdist, _st.reciprocal,
        _st.rayleigh, _st.rice, _st.recipinvgauss, _st.semicircular, _st.t, _st.triang, _st.truncexpon, _st.truncnorm, _st.tukeylambda,
        _st.uniform, _st.vonmises, _st.vonmises_line, _st.wald, _st.weibull_min, _st.weibull_max, _st.wrapcauchy
    ]

    # Best holders
    best_distribution = _st.norm
    best_params = (0.0, 1.0)
    best_sse = _np.inf

    # Estimate distribution parameters from data
    for distribution in DISTRIBUTIONS:

        # Try to fit the distribution
        try:
            # Ignore warnings from data that can't be fit
            with _warnings.catch_warnings():
                _warnings.filterwarnings('ignore')

                # fit dist to data
                params = distribution.fit(data)

                # Separate parts of parameters
                arg = params[:-2]
                loc = params[-2]
                scale = params[-1]

                # Calculate fitted PDF and error with fit in distribution
                pdf = distribution.pdf(x, loc=loc, scale=scale, *arg)
                sse = _np.sum(_np.power(y - pdf, 2.0))

                # if axis pass in add to plot
                try:
                    if ax:
                        _pd.Series(pdf, x).plot(ax=ax)
                except Exception:
                    pass

                # identify if this distribution is better
                if best_sse > sse > 0:
                    best_distribution = distribution
                    best_params = params
                    best_sse = sse

        except Exception:
            pass

    return (best_distribution.name, best_params)

def make_pdf(dist, params, size=10000):
    """Generate distributions's Propbability Distribution Function """

    # Separate parts of parameters
    arg = params[:-2]
    loc = params[-2]
    scale = params[-1]

    # Get sane start and end points of distribution
    start = dist.ppf(0.01, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.01, loc=loc, scale=scale)
    end = dist.ppf(0.99, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.99, loc=loc, scale=scale)

    # Build PDF and turn into pandas Series
    x = _np.linspace(start, end, size)
    y = dist.pdf(x, loc=loc, scale=scale, *arg)
    pdf = _pd.Series(y, x)

    return pdf


data = _pd.Series((3, 2, 4, 0, 0, 2, 2, 2, 1, 3, 9, 7, 12, 0, 1, 1, 1, 4, 3, 3, 3, 4, 2, 8, 3, 1, 5, 5, 2, 2, 1, 3, 3, 5, 1, 1, 2, 1, 4, 1, 4, 4, 0, 2, 0, 6, 7, 4, 1, 3, 1, 3, 4, 0, 1, 1, 1, 1, 3, 1, 0, 1, 2, 1, 1, 1, 3, 1, 1, 0, 4, 2, 1, 1, 0, 1, 1, 2, 2, 2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 2, 2, 1, 2, 2, 0, 0, 9, 4, 0, 2, 1, 2, 0, 5, 4, 3, 1, 9, 7, 3, 0, 2, 4, 2, 5, 2, 1, 2, 2, 1, 3, 0, 2, 1, 0, 2, 2, 0, 1, 3, 0, 5, 1, 1, 1, 3, 1, 2, 5, 0, 0, 2, 1, 1, 4, 1, 2, 5, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 2, 2, 2, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 3, 6, 1, 3, 1, 3, 2, 2, 3, 14, 0, 1, 1, 4, 1, 0, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 3, 0, 0, 2, 3, 3, 3, 1, 1, 2, 3, 3, 1, 1, 4, 2, 4, 1, 3, 1, 2, 1, 1, 0, 1, 2, 1, 1, 3, 1, 3, 1, 1, 1, 1, 6, 3, 1, 3, 2, 2, 1, 2, 1, 9, 5, 1, 1, 0, 2, 1, 1, 2, 0, 1, 2, 3, 2, 0, 1, 1, 2, 1, 1, 1, 0, 2, 3, 0, 1, 1, 6, 1, 0, 4, 3, 1, 6, 1, 1, 1, 0, 1, 1, 4, 4, 1, 3, 2, 1, 2, 4, 3, 1, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 2, 1, 2, 0, 3, 2, 4, 1, 2, 2, 0, 1, 1, 1, 1, 1, 3, 2, 1, 2, 1, 1, 1, 4, 0, 1, 3, 0, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 3, 1, 1, 2, 1, 1, 2, 1, 2, 4, 2, 1, 5, 4, 1, 1, 1, 1, 1, 0, 4, 0, 3, 3, 7, 3, 2, 0, 1, 3, 4, 2, 1, 1, 1, 3, 1, 1, 2, 0, 3, 2, 1, 1, 1, 0, 1, 2, 1, 3, 2, 3, 2, 2, 1, 1, 1, 0, 3, 1, 1, 0, 2, 4, 3, 3, 2, 0, 1, 1, 5, 2, 1, 1, 2, 4, 2, 2, 1, 6, 1, 4, 1, 2, 1, 1, 5, 4, 0, 3, 2, 1, 4, 6, 1, 1, 2, 1, 2, 2, 1, 3, 2, 2, 1, 3, 1, 3, 4, 5, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 4, 3, 2, 4, 1, 0, 5, 0, 3, 1, 3, 6, 0, 2, 2, 1, 3, 2, 0, 0, 1, 6, 1, 2, 4, 1, 1, 2, 1, 3, 1, 0, 5, 3, 3, 0, 2, 2, 2, 2, 0, 2, 2, 1, 3, 0, 4, 4, 0, 1, 3, 1, 3, 3, 0, 1, 3, 0, 1, 5, 0, 4, 3, 1, 1, 1, 1, 0, 4, 0, 0, 0, 5, 1, 0, 5, 2, 1, 0, 4, 0, 0, 0, 0, 4, 0, 2, 0, 0, 2, 2, 1, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 1, 0, 0, 6, 3, 2, 5, 0, 0, 0, 1, 3, 1, 0, 0, 4, 1, 1, 1, 2, 2, 1, 4, 0, 0, 4, 6, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4, 2, 1, 0, 0, 0, 0, 1, 2, 0, 0, 0, 5, 0, 0, 0, 1, 0, 0, 0, 3, 1, 1, 1, 2, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 1, 0, 3, 1, 1, 2, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 2, 1, 0, 3, 2, 3, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 4, 1, 1, 2, 3, 2, 1, 1, 1, 1, 1, 1, 2, 1, 4, 1, 1, 1, 1, 3, 1, 1, 0, 2, 1, 0, 2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

# Plot for comparison
plt.figure(figsize=(12, 8))
ax = data.plot(kind='hist', bins=50, alpha=0.5, color=plt.rcParams['axes.color_cycle'][1])
# Save plot limits
dataYLim = ax.get_ylim()

# Find best fit distribution
best_fit_name, best_fir_paramms = best_fit_distribution(data, 200, ax)
best_dist = getattr(_st, best_fit_name)

# Update plots
ax.set_ylim(dataYLim)
ax.set_title(u'Source venue count')
ax.set_xlabel(u'Source venue count')
ax.set_ylabel('Frequency')

# Make PDF
pdf = make_pdf(best_dist, best_fir_paramms)

# Display
plt.figure(figsize=(12,8))
ax = pdf.plot(lw=2, label='PDF', legend=True)
data.plot(kind='hist', bins=50, density=True, alpha=0.5, label='Data', legend=True, ax=ax)

param_names = (best_dist.shapes + ', loc, scale').split(', ') if best_dist.shapes else ['loc', 'scale']
param_str = ', '.join(['{}={:0.2f}'.format(k,v) for k,v in zip(param_names, best_fir_paramms)])
dist_str = '{}({})'.format(best_fit_name, param_str)

ax.set_title(u'Source venue count\n' + dist_str)
ax.set_xlabel(u'Source venue count')
ax.set_ylabel('Frequency')