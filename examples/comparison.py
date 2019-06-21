
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns
import pandas as pd
import numpy as np
import pickle


def align_yaxis(ax1, ax2):
    """Align zeros of the two axes, zooming them out by same ratio"""
    axes = np.array([ax1, ax2])
    extrema = np.array([ax.get_ylim() for ax in axes])
    tops = extrema[:, 1] / (extrema[:, 1] - extrema[:, 0])
    # Ensure that plots (intervals) are ordered bottom to top:
    if tops[0] > tops[1]:
        axes, extrema, tops = [a[::-1] for a in (axes, extrema, tops)]

    # How much would the plot overflow if we kept current zoom levels?
    tot_span = tops[1] + 1 - tops[0]

    extrema[0, 1] = extrema[0, 0] + tot_span * (extrema[0, 1] - extrema[0, 0])
    extrema[1, 0] = extrema[1, 1] + tot_span * (extrema[1, 0] - extrema[1, 1])
    [axes[i].set_ylim(*extrema[i]) for i in range(2)]


def find_effects(df, variable, output, min_phase=None):
    phases = sorted(set(df[variable]))

    if min_phase is not None:
        phases = [x for x in phases if x >= min_phase]
    averages = []
    stds = []
    for phase in phases:
        averages.append(df[df[variable] == phase][output].mean())
        stds.append(df[df[variable] == phase][output].std())
    return np.array(phases), np.array(averages), np.array(stds)


def process_frequencies(df):
    frequencies = sorted(set(df['Frequency']))
    print(frequencies)
    counter = -1
    for frequency in frequencies:
        df = df.replace(frequency, counter)
        counter += 1
    return df


# Scaling
scaling_bird = -2
scaling_sma = 3
variable = 'Phase'
# Calling DataFrame constructor on list
d_bird = pd.read_csv('altshuler_data.csv')
d_sma = pd.read_csv('sma_data.csv')

if variable == 'Frequency':
    d_bird = process_frequencies(d_bird)
    d_sma = process_frequencies(d_sma)
# Scaling
d_bird['Work'] = d_bird['Work']*10**scaling_bird
d_sma['Work'] = d_sma['Work']*10**scaling_sma

x_sma, av_sma, std_sma = find_effects(d_sma, variable, 'Work')
x_bird, av_bird, std_bird = find_effects(d_bird, variable, 'Work', -50)

fig, ax1 = plt.subplots()

ax2 = ax1.twinx()
ax1.fill_between(x_bird, av_bird - 2*std_bird, av_bird + 2*std_bird,
                 color='.4', alpha=0.2, lw=0)
ax1.fill_between(x_bird, av_bird - std_bird, av_bird + std_bird, color='.4',
                 alpha=0.2, lw=0)
# ax2.fill_between(x_sma, av_sma - 2*std_sma, av_sma + 2*std_sma, color='k', alpha=0.2)
# ax2.plot(x_sma, av_sma, 'k', lw=2)
# ax2.scatter(d_bird[variable], d_bird['Work'], c='b')
ax2.scatter(d_sma[variable], d_sma['Work'], c='k')
ax2.set_ylim([-5, 5.5])
align_yaxis(ax1, ax2)
ax1.set_xlabel(variable + ' (%)')
ax1.axhline(linewidth=1, color='0.4', linestyle='--')
ax1.set_ylabel('Work ($10^2$ W/kg)', color='b')
ax2.spines['left'].set_color('blue')
ax1.tick_params(axis='y', colors='blue')
ax2.set_ylabel('Work ($10^{-3}$ W/kg)', color='k')
plt.xticks(x_sma)  # [-50, -25, 0, 25, 50])
plt.show()
