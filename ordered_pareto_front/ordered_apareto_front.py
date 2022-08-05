from typing import List, Optional, Iterator
import matplotlib.pyplot as plt
import matplotlib as mpl
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
    color_gradient = 'viridis'

    # Create the plotting objects
    df = read_data()
    n_campaigns = len(df['campaign'].unique())
    figure: plt.Figure = plt.figure(figsize=(10, 6))
    axes: List[List[plt.Axes]] = [[], []]
    for i in range(2):
        for j in range(n_campaigns):
            ax = figure.add_subplot(2, n_campaigns, i * n_campaigns + j + 1)
            axes[i].append(ax)

    # Format figure
    figure.subplots_adjust(
        left=0.1,
        right=0.95,
        bottom=0.05,
        top=0.95,
        wspace=0.2,
        hspace=0.2,
    )

    # Plot the Pareto data
    y0_name = 'x3: temperature'
    y1_name = 'conductivity'
    for i in range(n_campaigns):

        ax = axes[0][i]
        df_c = df[df['campaign'] == i]
        df_c = df_c.sort_values(by='sample')
        y = df_c[[y0_name, y1_name]].to_numpy()

        # Generate the colors for the plot
        order = df_c['sample'].to_numpy()
        order_norm = order / max(order)
        cmap = mpl.colormaps.get(color_gradient)
        color = cmap(order_norm)
        fill_color = np.copy(color)
        fill_color[:, 3] = 0.85

        ax.scatter(
            y[:, 0],
            y[:, 1],
            s=20,
            c=fill_color,
            edgecolors=color,
            zorder=10
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
        ax.step(
            y0_pareto,
            y1_pareto,
            where='post',
            zorder=5,
            color='lightgrey',
            lw=1,
        )

        ax.fill_between(
            y0_pareto,
            lower_edge,
            y1_pareto,
            step='post',
            alpha=0.35,
            color='lightgray',
        )

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

            if j == 0:
                ax.set_xlabel('temperature (°C)')
                ax.set_ylabel('conductivity (S m⁻¹)')

    # Save
    name = os.path.basename(__file__).split('.')[0]
    figure.set_dpi(300)
    figure.savefig(f'{name}.png')
    # figure.savefig(f'{name}.svg')


if __name__ == '__main__':
    plot_data()
