import matplotlib.pyplot as plt
import matplotlib as mpl
from typing import List
import pandas as pd
import numpy as np
import os


def convert_to_conductivity(xrf_conductivity):
    """
    Convert from condxrf to conductivity
    :param xrf_conductivity: Units S / cps
    :return: S / m
    """

    # Define the slope that converts between cps and nm
    slope = 1.59605107323  # units of cps / nm

    # cpmdxrf has units of S / cps. Convert to S / nm
    conductivity_nm = xrf_conductivity / slope

    # Convert into conductivity_nm using the thin film formula
    conductivity_nm = conductivity_nm * np.log(2) / np.pi

    # Convert from units of S / nm to S / m
    conductivity_m = conductivity_nm * 1E9

    return conductivity_m


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
            dfs.append(idf)

    # Concatenate and convert conductance to conductivity
    df = pd.concat(dfs)
    df['conductivity'] = convert_to_conductivity(df['XRF-normalized conductance - mean'])
    return df


def plot_data():
    """
    Plot the processed campaign data in order of sampling.
    :return: None
    """

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
        left=0.05,
        right=0.95,
        bottom=0.05,
        top=0.95,
        wspace=0.2,
        hspace=0.15,
    )

    # Plot the Pareto data
    y0_name = 'x3: temperature'
    y1_name = 'conductivity'
    for i in range(n_campaigns):
        df_c = df[df['campaign'] == i]
        df_c = df_c.sort_values(by='sample')
        y0_data = df_c[y0_name].to_numpy()
        y1_data = df_c[y1_name].to_numpy()

        # Generate the colors for the plot
        order = df_c['sample'].to_numpy()
        order_norm = order / max(order)
        cmap = mpl.colormaps.get('magma')
        color = cmap(order_norm)
        fill_color = np.copy(color)
        fill_color[:, 3] = 0.75

        axes[0][i].scatter(
            y0_data,
            y1_data,
            s=20,
            c=fill_color,
            edgecolors=color,
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

    # Save
    name = os.path.basename(__file__).split('.')[0]
    figure.set_dpi(300)
    figure.savefig(f'{name}.png')
    # figure.savefig(f'{name}.svg')


if __name__ == '__main__':
    plot_data()
