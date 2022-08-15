import os
import pandas as pd
import numpy as np
from sklearn import gaussian_process as gp
import matplotlib.pyplot as plt
from matplotlib import colorbar
import matplotlib.image as mpimg
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import matplotlib.patches as mpatches
import matplotlib as mpl

# Shut up Pandas
pd.options.mode.chained_assignment = None

# Images [141, 125, 159, 155, 173]
# were sourced from 20190709_imaging_manu_graphics/imaging_fig_4_grid/2019-07-02_13-46-20/
# sample_{str(img).zfill(3)}/spincoated_slide_after_annealing1.jpg

render_images = True
pd.set_option("display.max_columns", 100)

font = {
    'family': 'arial',
    'size': 14,
}
mpl.rc('font', **font)


def run():
    """
    Create a single plot comparing mobility and image quality.
    :return: None
    """

    # Define some global constants
    ax_0 = 'ratio_round'
    ax_1 = 'anneal'
    res = 100
    levels = 10
    x0_buffer = 0.1
    x1_buffer = 0.1

    # Plotting configurations
    cmap = 'plasma_r'
    bar_cmap = 'plasma'
    ax_2 = 'Quality'
    bar_label = r'Dewetting score ($S_{dewet}$)'
    bar_bounds = ['Poor', 'Good']
    bar_label_offset = -25
    alpha_quality = 1e-3

    # Create the matplotlib objects
    figure: plt.Figure = plt.figure(figsize=(9, 6), dpi=400)

    ax_qual: plt.Axes = plt.subplot2grid((12, 65), (2, 3), colspan=35, rowspan=8)
    ax_qual_c: plt.Axes = plt.subplot2grid((12, 65), (2, 44), rowspan=8)
    ax_arrows: plt.Axes = plt.subplot2grid((1, 65), (0, 45), colspan=8)
    ax_images: plt.Axes = plt.subplot2grid((1, 65), (0, 54), colspan=10)

    figure.subplots_adjust(
        left=0.05,
        right=0.98,
        top=0.98,
        bottom=0.02,
    )

    # Import the data
    df_quality = pd.read_csv('morphology_data.csv')

    # Downsample
    # selection = '0'
    df_plot = df_quality[(df_quality['tbp_frac'] >= 0) & (df_quality['tbp_frac'] < 0.05)]
    # selection = '1'
    # df_plot = df_quality[(df_quality['tbp_frac'] > 0.05) & (df_quality['tbp_frac'] < 0.12)]
    # selection = '2'
    # df_plot = df_quality[(df_quality['tbp_frac'] > 0.12) & (df_quality['tbp_frac'] < 0.183)]
    # selection = '3'
    # df_plot = df_quality[(df_quality['tbp_frac'] > 0.183) & (df_quality['tbp_frac'] < 0.25)]
    # selection = '4'
    # df_plot = df_quality[(df_quality['tbp_frac'] > 0.25) & (df_quality['tbp_frac'] < 0.30)]
    # df_plot = df_quality
    # selection = ''

    # Round
    df_plot['ratio_round'] = round(df_plot['ratio'] / 0.2) * 0.2

    # First normalize the data and fit the GP
    x0_min = df_plot[ax_0].min()
    x0_max = df_plot[ax_0].max()
    x1_min = df_plot[ax_1].min()
    x1_max = df_plot[ax_1].max()
    x0_range = x0_max - x0_min
    x1_range = x1_max - x1_min

    # Create the domain for fitting
    x = np.vstack(
        (
            (df_plot[ax_0].values - x0_min) / x0_range,
            (df_plot[ax_1].values - x1_min) / x1_range,
        )
    ).T
    y = df_plot[ax_2].values

    # Fit the model
    model = gp.GaussianProcessRegressor(
        alpha=alpha_quality
    )
    model.fit(x, y)

    # Sample the model
    x0 = np.linspace(0 - x0_buffer, 1 + x0_buffer, res)
    x1 = np.linspace(0 - x1_buffer, 1 + x1_buffer, res)
    x0_g, x1_g = np.meshgrid(x0, x1)
    x0_f = x0_g.flatten()
    x1_f = x1_g.flatten()
    x = np.vstack((x0_f, x1_f)).T
    y = model.predict(x)

    # Rescale
    x0_gs = x0_g * x0_range + x0_min
    x1_gs = x1_g * x1_range + x1_min

    # Plot the scatter
    ax_qual.scatter(
        df_plot[ax_0],
        df_plot[ax_1],
        c=df_plot[ax_2],
        cmap=cmap,
        linewidths=1.5,
        edgecolor='white',
        s=120,
        zorder=2,
    )

    # # Add contours
    ax_qual.contourf(
        x0_gs,
        x1_gs,
        y.reshape((res, res)),
        levels=levels,
        alpha=0.3,
        cmap=cmap,
        zorder=0,
    )

    ax_qual.contour(
        x0_gs,
        x1_gs,
        y.reshape((res, res)),
        levels=levels,
        cmap=cmap,
        zorder=1,
        linewidths=2,
    )

    # Format the color bar
    bar = colorbar.ColorbarBase(
        ax_qual_c,
        cmap=plt.get_cmap(bar_cmap),
        ticks=[0, 1],
    )
    bar.set_ticklabels(bar_bounds)
    bar.ax.yaxis.tick_left()

    bar.set_label(bar_label)
    bar.ax.yaxis.set_label_position('left')
    bar.ax.yaxis.labelpad = bar_label_offset

    # Add the secondary axis
    # bar_right: plt.Axes = bar.ax.twinx()
    # bar_right.set_ylim(0, 1)
    # bar_right.set_yticks(np.linspace(0, 1, 5))
    # bar_right.set_yticklabels([''] * 5)
    # bar_right.tick_params(length=36)

    # For each image
    for i in range(5):

        if render_images:

            # Add the image
            arr_img = mpimg.imread(f'raw_images/{4-i}.jpg')

            # Make image brighter
            bright_scale = 1.75
            arr_img_scaled = arr_img/255 * bright_scale
            arr_img_scaled = np.where(arr_img_scaled < 1, arr_img_scaled, 1)

            offset_img = OffsetImage(
                arr_img_scaled,
                zoom=0.025,  # Change this for the size of the images
            )

            an_img = AnnotationBbox(
                offset_img,
                (0.5, 0.1 + 0.2 * i),
                bboxprops=dict(
                    edgecolor='none'
                ),

            )
            ax_images.add_artist(an_img)

        # Add the arrow
        ax_arrows.add_patch(
            mpatches.FancyArrowPatch(
                # (x,y) of tail, 0 to 1.
                (1, (1 / 10) + (8 / 10) / 4 * i),
                # (x,y) of head, 0 to 1.
                (0.05, (2 / 12) + i * (1/5 * 10/12)),
                mutation_scale=20,
                linewidth=0,
                facecolor='lightgrey'
            )
        )

    # Formatting
    ax_qual.set_xlabel('Dopant:HTM ($\mathit{n/n}$)')
    ax_qual.set_ylabel('Annealing time ($\mathit{s}$)')

    x0_pmin = -0.05
    x0_pmax = 1.05
    x1_pmin = -10
    x1_pmax = 260
    ax_qual.set_xlim(x0_pmin, x0_pmax)
    ax_qual.set_ylim(x1_pmin, x1_pmax)
    ax_qual.set_xticks(np.linspace(0, 1, 6))
    ax_qual.set_yticks(np.linspace(0, 250, 6))
    # ax_qual.set_xticklabels([0, '', '', '', '', 1])
    # ax_qual.set_yticklabels([0, '', '', '', '', 250])

    ax_arrows.axis('off')
    ax_images.axis('off')

    figname = 'morphology_data'
    figure.savefig(f'{figname}.png')
    figure.savefig(f'{figname}.svg')
    os.system(f'open {figname}.png')


if __name__ == '__main__':
    run()
