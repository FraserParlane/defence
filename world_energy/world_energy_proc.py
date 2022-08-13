import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from matplotlib import ticker
import os

# Configure display
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000)

# Default font
mpl.rcParams['font.sans-serif'] = 'Roboto'
mpl.rcParams['font.weight'] = 'medium'
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False


def load_data() -> pd.DataFrame:

    # This date originates from BP's Statistical Review of World Energy
    # https://www.bp.com/en/global/corporate/energy-economics/statistical-review-of-world-energy.html

    # Data manually summarised from .xlsx here:
    # https://docs.google.com/spreadsheets/d/1nAkRHbUmsCjcayQHBPRB282LRbyMtHEC6xL2YR7IMQY

    # Read in raw data from csv
    df_mtoeyr = pd.read_csv('data.csv').set_index('Year').T

    # Make index an integer
    df_mtoeyr.index = df_mtoeyr.index.astype('int64')

    # Convert to power
    mtoeyr_to_twhyr = 11.63
    twhyr_to_twhh = 1 / (24 * 365)
    conv = mtoeyr_to_twhyr * twhyr_to_twhh
    df_tw = df_mtoeyr * conv

    # Create a total column.
    energy_names = ['Oil', 'Gas', 'Coal', 'Nuclear', 'Hydro', 'Solar', 'Wind', 'Other']
    fossil_names = ['Oil', 'Gas', 'Coal']
    renew_names  = ['Wind', 'Solar', 'Other']
    other_names = ['Hydro', 'Nuclear']
    nonfossil_names = ['Wind', 'Solar', 'Other', 'Hydro', 'Nuclear']

    # Create summary colums
    df_tw['Total'] = df_tw[energy_names].sum(axis=1)
    df_tw['Fossil'] = df_tw[fossil_names].sum(axis=1)
    df_tw['Nonfossil'] = df_tw[nonfossil_names].sum(axis=1)
    df_tw['Renew'] = df_tw[renew_names].sum(axis=1)
    df_tw['NuclearHydro'] = df_tw[other_names].sum(axis=1)

    # Return as TW
    return df_tw


def load_predict():

    # https://docs.google.com/spreadsheets/d/15jLVwE5MGdgwCSmu8vOpY693ceZHLoLydtpeMd1ABGY

    df = pd.read_csv('prediction.csv').set_index('Year')
    return df

def proportion():

    df = load_data()

    # Calculate percent contributions
    df_frac = df.div(df.Total, axis=0)

    # Names and colors
    cats = {
        'Solar': 'orangered',
        'Wind': 'tomato',
        'Other': 'Salmon',
        'Nuclear': 'dimgray',
        'Hydro': 'gray',
        'Oil': 'dodgerblue',
        'Gas': 'deepskyblue',
        'Coal': 'turquoise',

    }

    # Begin plotting
    figure: plt.Figure = plt.figure()
    axes: plt.Axes = figure.add_subplot(1, 1, 1)

    # baseline
    base = np.zeros(df_frac.shape[0])

    for name, color in cats.items():

        # Increase
        new_base = base + df_frac[name]

        # Fill
        axes.fill_between(
            df_frac.index,
            base,
            new_base,
            color=color,
        )

        # White line
        axes.plot(
            df_frac.index,
            new_base,
            color='white',
            linewidth=0.5,
        )



        # Update
        base = new_base

    # Formatting

    # Axes labels
    axes.set_ylabel('Source of energy consumed')
    axes.set_yticks([])

    # get rid of the frame
    for spine in axes.spines.values():
        spine.set_visible(False)

    # Bounds
    axes.set_xlim(min(df.index), max(df.index))
    axes.set_ylim(0, 1)

    # Remove ticks
    axes.tick_params(axis=u'both', which=u'both', length=10, color='white')

    # Plot
    figure.savefig('proportion.png')
    plt.show()


def abs_difference():

    df = load_data() / 1000
    diff = df.diff()

    figure: plt.Figure = plt.figure(figsize=(8,3), dpi=600)
    axes: plt.Axes = figure.add_subplot()

    sources = {
        'Renew': 'dodgerblue',
        'Fossil': '#ff4a59',
        'Total': '#4d4d4d',
    }

    for source, color in sources.items():
        axes.plot(
            diff.index,
            diff[source],
            label=source,
            color=color,
            linewidth=3,
        )

    # Formatting
    axes.set_xlim(2000, 2018.2)
    axes.set_ylabel('Annual change in global\nconsumption (GWh)', weight='medium')

    # get rid of the frame
    for spine in axes.spines.values():
        spine.set_visible(False)

    # Make ticks white
    axes.tick_params(axis=u'both', which=u'both', length=10, color='white')

    # Make the grid
    axes.yaxis.set_minor_locator(ticker.MultipleLocator(2))
    axes.yaxis.set_major_locator(ticker.MultipleLocator(10))
    axes.yaxis.set_minor_formatter(ticker.FormatStrFormatter('%.0f'))
    axes.xaxis.set_major_locator(ticker.MultipleLocator(2))

    axes.yaxis.grid(
        linewidth='0.5',
        color='lightgrey',
        which='minor'
    )

    axes.yaxis.grid(
        linewidth='1',
        color='darkgrey',
        which='major'
    )

    # Padding
    figure.subplots_adjust(
        right=0.85,
        bottom=0.2,
        top=0.95,
    )

    # Prepare annotation labels
    annotations = {
        'Total': 'Total',
        'Fossil': 'Fossil fuels',
        'Renew': 'Renewables',
    }

    for data, label in annotations.items():
        axes.text(
            2018.5,
            diff[data].to_numpy()[-1],
            label,
            color=sources[data],
            verticalalignment='center',
        )

    name = 'abs_difference.png'
    figure.savefig(name)
    os.system(f'open {name}')


def consumption():

    df = load_data()

    figure: plt.Figure = plt.figure(figsize=(8,4), dpi=600)
    axes: plt.Axes = figure.add_subplot()

    sources = {
        'Renew': 'dodgerblue',
        'Fossil': '#ff4a59',
        'Total': '#4d4d4d',
    }

    for source, color in sources.items():
        axes.plot(
            df.index,
            df[source],
            label=source,
            color=color,
            linewidth=3,
        )

    # Formatting
    axes.set_xlim(2000, 2018.2)
    axes.set_ylabel('Power consumption (TW)', weight='medium')

    # get rid of the frame
    for spine in axes.spines.values():
        spine.set_visible(False)

    # Make ticks white
    axes.tick_params(axis=u'both', which=u'both', length=10, color='white')

    # Make the grid
    axes.yaxis.set_major_locator(ticker.MultipleLocator(5))
    axes.xaxis.set_major_locator(ticker.MultipleLocator(2))

    axes.yaxis.grid(
        linewidth='0.5',
        color='lightgrey',
        which='major'
    )

    # Padding
    figure.subplots_adjust(
        right=0.85,
        bottom=0.2,
        top=0.95,
    )

    # Prepare annotation labels
    annotations = {
        'Total': 'Total',
        'Fossil': 'Fossil fuels',
        'Renew': 'Renewables',
    }

    for data, label in annotations.items():
        axes.text(
            2018.5,
            df[data].to_numpy()[-1],
            label,
            color=sources[data],
            verticalalignment='center',
        )

    name = 'consumption.png'
    figure.savefig(name)
    os.system(f'open {name}')


def change():

    df = load_data()

    # Calculate percent change, diff.
    df_e_per = df.pct_change().replace(np.inf, np.nan) * 100
    df_e_diff = df.diff()

    # Calculate percent contribution of fossil, renew
    df_e_diff['Fossil_per'] = df_e_diff.Fossil / df_e_diff.Total
    df_e_diff['Renew_per'] = df_e_diff.Renew / df_e_diff.Total

    # Begin plotting
    figure: plt.Figure = plt.figure(figsize=(7,3))
    axes: plt.Axes = figure.add_subplot(1, 1, 1)

    axes.plot(
        df_e_per.Total,
        label='Total'
    )

    # Formatting
    axes.set_xlim(2000, 2018)
    axes.set_xlabel('Year')
    axes.set_ylabel('Percent change, annual')
    axes.legend()

    # get rid of the frame
    for spine in axes.spines.values():
        spine.set_visible(False)

    # Make ticks white
    axes.tick_params(axis=u'both', which=u'both',length=10, color='white')

    # Make the grid
    y_spacing_minor = 2
    y_spacing_major = 10
    axes.yaxis.set_minor_locator(ticker.MultipleLocator(y_spacing_minor))
    axes.yaxis.set_major_locator(ticker.MultipleLocator(y_spacing_major))
    axes.yaxis.set_minor_formatter(ticker.FormatStrFormatter('%.0f'))

    axes.yaxis.grid(
        linewidth='0.5',
        color='lightgrey',
        which='minor'
    )

    axes.yaxis.grid(
        linewidth='2',
        color='lightgrey',
        which='major'
    )

    plt.show()


def consumption_projected():

    df = load_data()

    figure: plt.Figure = plt.figure(figsize=(8,4), dpi=600)
    axes: plt.Axes = figure.add_subplot()

    sources = {
        'NuclearHydro': 'lightgrey',
        'Renew': 'dodgerblue',
        'Fossil': '#ff4a59',
    }

    # Make a rising base
    base = np.zeros(df.shape[0])

    for source, color in sources.items():

        # Increase
        new_base = base + df[source]

        axes.plot(
            df.index,
            new_base,
            label=source,
            color=color,
            linewidth=3,
        )

        axes.fill_between(
            df.index,
            base,
            new_base,
            color=color,
            alpha=0.5,
            linewidth=0,

        )

        # Update
        base = new_base

    # Formatting
    axes.set_xlim(1965, 2050)
    axes.set_ylim(0, 30)
    axes.set_ylabel('Power consumption (TW)', weight='medium')

    # get rid of the frame
    for spine in axes.spines.values():
        spine.set_visible(False)

    # Make ticks white
    axes.tick_params(axis=u'both', which=u'both', length=10, color='white')

    # Make the grid
    axes.yaxis.set_major_locator(ticker.MultipleLocator(5))
    axes.xaxis.set_major_locator(ticker.MultipleLocator(10))

    axes.yaxis.grid(
        linewidth='0.5',
        color='lightgrey',
        which='major'
    )

    # Padding
    figure.subplots_adjust(
        right=0.85,
        bottom=0.2,
        top=0.95,
    )

    name = 'consumption_projected.svg'
    figure.savefig(name)
    os.system(f'open {name}')


def fossil_nonfossil():

    # Get data
    df = load_data()
    df_p = load_predict()

    # Scale the predict data so that it is inline with the history data
    for i in ['Total', 'Fossil', 'Nonfossil']:
        df_p[i] = df_p[i].multiply(df[i].iloc[-1] / df_p[i].iloc[0])

    # Create figure
    figure: plt.Figure = plt.figure(figsize=(6,3), dpi=600)
    axes: plt.Axes = figure.add_subplot()

    sources = {
        0: {
            'id': 'Nonfossil',
            'color': 'dodgerblue',
            'alpha': 0.4,
        },
        1: {
            'id': 'Fossil',
            'color': '#444444',
            'alpha': 0.2,
        },
    }

    # Make a rising base
    base = np.zeros(df.shape[0])

    for i, s in sources.items():

        # Increase
        new_base = base + df[s['id']]

        axes.plot(
            df.index,
            new_base,
            label=s['id'],
            color=s['color'],
            solid_capstyle='round',
            linewidth=3,
        )

        axes.fill_between(
            df.index,
            base,
            new_base,
            color=s['color'],
            alpha=s['alpha'],
            linewidth=0,

        )

        # Update
        base = new_base

    # Update forecast
    axes.plot(
        df_p.index,
        df_p['Total'],
        color=sources[1]['color'],
        solid_capstyle='round',
        linewidth=3,
    )

    # Update nonfossil
    axes.plot(
        df_p.index,
        df_p['Nonfossil'],
        color=sources[0]['color'],
        solid_capstyle='round',
        linewidth=3,
        alpha=0.4,
    )

    # Draw upward arrow

    verts = [
        (df.index[-1], df['Nonfossil'].iloc[-1]),
        (2027, 4),
        (2037, 8),
        (2042.5, 15),
    ]
    codes = [
        Path.MOVETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
    ]
    path = Path(verts, codes)
    patch = patches.PathPatch(path, facecolor='none', lw=3, edgecolor=sources[0]['color'])
    axes.add_patch(patch)

    # Arrowhead
    apos = (verts[3][0]+0.7, verts[3][1]+1)
    arrow = patches.FancyArrowPatch(
        apos,
        (apos[0] + 0.3, apos[1] + 0.45),
        mutation_scale=25,
        linewidth=0,
        color=sources[0]['color'],
    )
    axes.add_patch(arrow)

    # Add circle
    axes.scatter(
        df_p.index[-1],
        df_p['Total'].iloc[-1],
        s=75,
        clip_on=False,
        zorder=100,
        edgecolors=sources[1]['color'],
        linewidths=3,
        color='white',

    )

    # Add text
    axes.text(
        2020, 1.2,
        'Non-fossil fuels',
        color=sources[0]['color'],
        horizontalalignment='left',
        verticalalignment='center',
        fontweight='bold',
    )

    axes.text(
        2020, 12,
        'Fossil fuels',
        color=sources[1]['color'],
        horizontalalignment='left',
        verticalalignment='center',
        fontweight='bold',
    )

    # Add little dot arrow

    for y, color in zip([1.2, 12], [sources[0]['color'], sources[1]['color']]):
        axes.scatter(2016, y, c='white', s=20)
        axes.plot([2016, 2019], [y, y], color='white', linewidth=3)
        axes.plot([2016, 2019], [y, y], color=color, linewidth=1.5)
        axes.scatter(2016, y, c=color, s=8, zorder=100)


    axes.text(
        2051,
        29,
        'Carbon neutrality by 2050 to\nlimit global heating to 1.5°C\n(IPCC criterion)',
        horizontalalignment='center',
        color=sources[1]['color'],
    )

    axes.text(
        2056,
        df_p['Nonfossil'].iloc[-1],
        'Current\nforecast',
        verticalalignment='center',
        horizontalalignment='center',
        color=sources[0]['color'],
    )

    axes.text(
        2051,
        16.5,
        'Improvement\nneeded',
        verticalalignment='center',
        horizontalalignment='center',
        color=sources[0]['color'],
    )

    # Formatting
    axes.set_xlim(1965, 2050)
    axes.set_ylim(0, 30)
    axes.set_ylabel('Total global power consumption (TW)', weight='medium')

    # Determine the spacing
    axes.yaxis.set_major_locator(ticker.MultipleLocator(10))
    axes.xaxis.set_major_locator(ticker.MultipleLocator(25))

    # Padding
    figure.subplots_adjust(
        right=0.83,
        bottom=0.1,
        top=0.85,
        left=0.12,
    )

    # Save
    name = 'fossil_nonfossil.png'
    figure.savefig(name)
    os.system(f'open {name}')


if __name__ == '__main__':
    fossil_nonfossil()