import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os


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

    # Concatenate and return
    df = pd.concat(dfs)
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
    axes = [[], []]
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
        wspace=0.05,
        hspace=0.05,
    )

    # Save
    name = os.path.basename(__file__).split('.')[0]
    figure.set_dpi(300)
    figure.savefig(f'{name}.png')
    figure.savefig(f'{name}.svg')


if __name__ == '__main__':
    plot_data()
