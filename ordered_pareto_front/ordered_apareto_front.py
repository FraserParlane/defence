from typing import List, Optional, Iterator
import matplotlib.pyplot as plt
from matplotlib import colorbar
import matplotlib as mpl
from tqdm import tqdm
import pandas as pd
import numpy as np
import operator
import os


def convert_to_conductivity(xrf_conductivity):
    """
    Convert from condxrf to conductivity
    :param xrf_conductivity: Units S / cps
    :return: S / m
    """

    # Define the slope that converts between cps and nm
    slope = 1.59605107323  # units of cps / nm

    # xrf_conductivity has units of S / cps. Convert to S / nm
    conductivity_nm = xrf_conductivity / slope

    # Convert into conductivity_nm using the thin film formula
    conductivity_nm = conductivity_nm * np.log(2) / np.pi

    # Convert from units of S / nm to S / m
    conductivity_m = conductivity_nm * 1E9

    return conductivity_m


def pareto_bool(
        y: np.ndarray,
        strict: bool = False,
        omax: Optional[Iterator[bool]] = None
) -> np.ndarray:
    """
    Generate the Pareto front mask for an array
    :param y: The input of shape n_samples x m_dimensionality
    :param strict: will not include points that are in between points on the Pareto front
    :param omax: An iterator of bools determining which objectives should be maximized. If
    None, all will be maximized.
    :return:
    """

    # Flip signs if needed
    y = np.copy(y)
    omax = np.full(y.shape[1], True) if omax is None else omax
    mask = ~np.array([omax, ] * len(y))
    y[mask] = -y[mask]

    # Calculate Pareto bool
    comp = operator.le if strict else operator.lt
    return ~np.array([np.any(np.prod(comp(y[i], np.delete(y, i, axis=0)), axis=1, dtype=bool)) for i in range(len(y))])


def calc_hypervolume(
        y: np.ndarray,
):
    """
    Calculates the hypervolume of an array. Note that this only works for 2D
    arrays. The array must be scaled such that the reference point is 0. This
    function should only be passed the Pareto array, not all the
    observations
    :param y: An array of shape samples x dimensions
    :return: float
    """

    # Make a copy of the array
    yc = np.copy(y)

    # Sort the data to be first ascending in x (col 0), and then descending in
    # y (col 1). First, make col 1 neg, sort by col 1 ascending, sort by col 1
    # ascending, and then make col 1 pos.
    # tstart = time.time()
    yc[:, 1] *= -1
    yc = yc[np.lexsort((yc[:, 1], yc[:, 0]))]
    yc[:, 1] *= -1

    # Determine the lower reference point for each rectangle integration
    yl = np.concatenate(([[0, 0]], yc[:-1]))
    yl[:, 1] = 0

    # Sum areas
    a = np.sum(np.prod(yc - yl, axis=1))

    return a


def pareto_bool_iter(
        y: np.ndarray,
        strict: bool = False,
        omax: Optional[Iterator[bool]] = None,
) -> np.ndarray:
    """
    Iteratively assess the Pareto front for an array
    :param y: The input of shape n_samples x m_dimensionality
    :param strict: will not include points that are in between points on the
    Pareto front
    :param omax: An iterator of bools determining which objectives should be
    maximized. If None, all will be maximized.
    :return: An array of length n_samples. Each integer in the array indicates
    when that observation last had Pareto dominance. For example array[2] = 3
    means that the second observation last had dominance at the third iteration.
    np.nan means the observation never had Pareto dominance.
    """

    # Get the length of the array
    length = y.shape[0]

    # Create a place to store the values
    pbool_idx = np.repeat(np.nan, length).astype('object')

    # Initiate the first point, which must be a Pareto point
    pbool_idx[0] = 0

    # Create the iterative dataset, and indexes for this data
    pdata = y[0][None, :]
    pidx = np.array([0])

    # Create an array that can be used to flip omax polarity
    if omax is None:
        pol = np.array([1] * y.shape[1])
    else:
        pol = np.array(omax).astype(int) * 2 - 1

    # For each remaining point
    for i in tqdm(range(1, length)):

        # Test to see if the Pareto front needs to be calculated
        comp = operator.le if strict else operator.lt
        if np.any(np.all(comp(y[i], pdata * pol), axis=1)):
            # Update arrays
            pbool_idx[pidx] = i

            # Skip Pareto calculation
            continue

        # Update the pdata and pidx prior to Pareto analysis
        pdata = np.vstack((pdata, y[i]))
        pidx = np.append(pidx, i)

        # Test Pareto
        pbool = pareto_bool(
            y=pdata,
            strict=strict,
            omax=omax,
        )

        # Update the pdata, and the pdata index based on the Pareto analysis
        pdata = pdata[pbool]
        pidx = pidx[pbool]

        # Update the master list
        pbool_idx[pidx] = i

    return pbool_idx


def calc_hypervolume_iter(
        y: np.ndarray,
        strict: bool = True,
) -> np.ndarray:
    """
    Calculate the change in hypervolume. Note that this function ingests all
    the data, not just the Pareto front. (Unlike calc_hypervolume()). Note that
    the data must be scaled such that 0 is the reference point
    :param y: An array of shape samples x dimensions
    :param strict: will not include points that are in between points on the
    Pareto front.
    :return: An array of length samples.
    """

    # Create an array in which to store the hypervolumes
    length = len(y)
    result = np.repeat(np.nan, length)

    # Get the Pareto bool iter. Each value indicates where that value was last
    # Pareto dominant.
    pbool_idx = pareto_bool_iter(
        y=y,
        strict=strict,
    )

    # For each observation
    for i in range(length):
        # Get the indices of the Pareto front
        pbool = pbool_idx[:i + 1] >= i

        # Calculate the hypervolume
        hv = calc_hypervolume(y[:i + 1][pbool])

        # Store the hypervolume
        result[i] = hv

    # Return
    return result


def read_data():
    """
    Read in the processed campaign data and concatenate.
    :return: df
    """

    # Read in each processed
    dfs = []
    for i, name in enumerate(os.listdir('data')):
        if name.endswith('.csv'):
            idf = pd.read_csv(f'data/{name}')
            idf['campaign'] = i

            # Calculate conductivity
            idf['conductivity'] = convert_to_conductivity(idf['XRF-normalized conductance - mean'])

            # Get Pareto front
            y = idf[['conductivity', 'x3: temperature']].to_numpy()
            idf['pareto'] = pareto_bool(
                y=y,
                omax=[True, False],
            )

            dfs.append(idf)

    # Concatenate and convert conductance to conductivity
    df = pd.concat(dfs)

    return df


def plot_data():
    """
    Plot the processed campaign data in order of sampling.
    :return: None
    """

    # Plotting constants
    lower_edge = -100
    upper_edge = 500
    color_gradient = 'viridis_r'
    cmap = mpl.colormaps.get(color_gradient)

    # Create the plotting objects
    df = read_data()
    n_campaigns = len(df['campaign'].unique())
    figure: plt.Figure = plt.figure(figsize=(10, 6))
    axes: List[List[plt.Axes]] = [[], []]
    for i in range(2):
        for j in range(n_campaigns):
            ax_0 = figure.add_subplot(2, n_campaigns, i * n_campaigns + j + 1)
            axes[i].append(ax_0)

    # Format figure
    figure.subplots_adjust(
        left=0.1,
        right=0.95,
        bottom=0.1,
        top=0.95,
        wspace=0.2,
        hspace=0.2,
    )

    # Plot the Pareto data
    y0_name = 'x3: temperature'
    y1_name = 'conductivity'
    for i in range(n_campaigns):

        ax_0 = axes[0][i]
        ax_1 = axes[1][i]
        df_c = df[df['campaign'] == i]
        df_c = df_c.sort_values(by='sample')
        y = df_c[[y0_name, y1_name]].to_numpy()

        # Generate the colors for the plot
        order = df_c['sample'].to_numpy()
        order_norm = order / max(order)
        color = cmap(order_norm)
        fill_color = np.copy(color)
        fill_color[:, 3] = 0.75

        ax_0.scatter(
            y[:, 0],
            y[:, 1],
            s=20,
            c='white',
            edgecolor='white',
            zorder=9,
            linewidth=0,
        )

        ax_0.scatter(
            y[:, 0],
            y[:, 1],
            s=20,
            c=fill_color,
            edgecolors=color,
            zorder=10,
            linewidth=1.5,
        )

        # Pareto front
        y_pareto = y[df_c['pareto']]
        y0_sort = np.argsort(y_pareto[:, 0])
        y1_sort = np.argsort(y_pareto[:, 1])
        y0_pareto = y_pareto[y0_sort, 0]
        y1_pareto = y_pareto[y1_sort, 1]
        y0_pareto = np.concatenate([[min(y0_pareto)], y0_pareto, [upper_edge]])
        y1_pareto = np.concatenate([[lower_edge], y1_pareto, [max(y1_pareto)]])

        # Plot Pareto front
        ax_0.step(
            y0_pareto,
            y1_pareto,
            where='post',
            zorder=5,
            color='lightgrey',
            lw=1,
        )

        ax_0.fill_between(
            y0_pareto,
            lower_edge,
            y1_pareto,
            step='post',
            alpha=0.35,
            color='lightgray',
        )

        # Calculate the iterative hypervolume. Normalize the data (globally)
        # first. Invert the temperature data for a relevant reference point.
        y_global = df[[y0_name, y1_name]].to_numpy()
        y_min = y_global.min(axis=0)
        y_max = y_global.max(axis=0)
        y_norm = (y - y_min) / (y_max - y_min)
        y_norm[:, 0] = 1 - y_norm[:, 0]
        hv = calc_hypervolume_iter(y=y_norm)

        # Plot hv improvement on each plot
        for ax in axes[1]:
            ax.step(
                np.arange(len(hv)),
                hv,
                where='post',
                lw=1,
                color='lightgrey',
                zorder=1,
            )
        ax_1.step(
            np.arange(len(hv)),
            hv,
            where='post',
            lw=5,
            color='#FFFFFF',
            zorder=9,
        )
        ax_1.step(
            np.arange(len(hv)),
            hv,
            where='post',
            lw=1.5,
            color='#333333',
            zorder=10,
        )

    # Add color bar to plot
    c_ax = figure.add_axes([0.14, 0.92, 0.1, 0.015])
    bar = colorbar.ColorbarBase(
        c_ax,
        cmap=cmap,
        orientation='horizontal',
        ticks=[0, 1],
    )

    # Format bar axis
    bar.set_ticklabels(['first', 'last'])
    bar.outline.set_visible(False)
    bar.set_label('sampling order', labelpad=-35)

    # Format each axes
    for i in range(2):
        for j in range(n_campaigns):
            ax = axes[i][j]

            # Remove bars
            for pos in ['top', 'right']:
                ax.spines[pos].set_visible(False)
            if j != 0:
                ax.spines['left'].set_visible(False)
                ax.get_yaxis().set_visible(False)

            # Scale top row
            if i == 0:
                ax.set_xlim(165, 290)
                ax.set_ylim(-5, 130)
                ax.set_xticks(np.linspace(180, 280, 3))
                ax.set_yticks(np.linspace(0, 120, 4))

            if i == 1:
                ax.set_xlim(-5, 80)
                ax.set_xticks(np.linspace(0, 75, 4))
                ax.set_ylim(0, 0.5)

            # If top left
            if i == 0 and j == 0:
                ax.set_xlabel('temperature (°C)')
                ax.set_ylabel('conductivity (S m⁻¹)')

            # If bottom left
            if i == 1 and j == 0:
                ax.set_xlabel('sample')
                ax.set_ylabel('normalized hypervolume')
                ax.set_yticks([0, 0.5])
                ax.set_yticklabels(['min', 'max'])

    # Save
    name = os.path.basename(__file__).split('.')[0]
    figure.set_dpi(300)
    figure.savefig(f'{name}.png')
    figure.savefig(f'{name}.svg')


if __name__ == '__main__':
    plot_data()
