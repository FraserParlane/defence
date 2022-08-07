from sklearn.gaussian_process import GaussianProcessRegressor
import matplotlib.pyplot as plt
import numpy as np
import os

# Create two surfaces to compare grid and optimization sampling.


def run():

    # Create noisy training data and fit GP
    n_train = 10
    np.random.seed(7)
    x_train = np.random.rand(n_train, 2)
    y_train = np.random.rand(n_train, 1)
    gp = GaussianProcessRegressor()
    gp.fit(x_train, y_train)

    # Sample GP for surface
    n_sample = 100
    xi_test = np.linspace(0, 1, n_sample)
    xi, xj = np.meshgrid(xi_test, xi_test)
    x_test = np.vstack((xi.flatten(), xj.flatten())).T
    y_test = gp.predict(x_test)
    y_test = y_test.reshape(n_sample, n_sample)

    # Create the figure objects
    figure: plt.Figure = plt.figure(
        dpi=300,
        figsize=(10, 5)
    )
    ax_0: plt.Axes = figure.add_subplot(1, 2, 1)
    ax_1: plt.Axes = figure.add_subplot(1, 2, 2)

    # Formatting constants
    data = (xi, xj, y_test)
    kwargs = {
        'cmap': 'plasma',
        'levels': 10,
    }

    # Plot the surfaces
    for ax in [ax_0, ax_1]:
        ax.contour(
            *data,
            **kwargs,
            linewidths=1.5,
            linestyles=":",
        )
        ax.contour(
            *data,
            **kwargs,
            linewidths=1.5,
            alpha=0.5,
        )
        ax.contourf(
            *data,
            **kwargs,
            alpha=0.2,
        )

    # Format
    for ax in [ax_0, ax_1]:
        ax.set_aspect('equal')
        for pos in ['left', 'right', 'top', 'bottom']:
            ax.spines[pos].set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    # Save
    name = os.path.basename(__file__).split('.')[0]
    figure.savefig(f'{name}.png')
    figure.savefig(f'{name}.svg')


if __name__ == '__main__':
    run()
