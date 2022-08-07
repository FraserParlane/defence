import matplotlib.patches as patches
import matplotlib.pyplot as plt
from typing import List
import pandas as pd
import numpy as np
import os

# A plot of the complexity of steel over time. See:
# https://docs.google.com/document/d/1ZkReceEGZomda2GGzVP1f2HIrID8KVW9nJ3OUeg8woA/edit


# Define the compositions of the steels
class Element:
    """
    One element of a steel.
    """
    def __init__(
            self,
            color: str,
            frac: float,
    ):
        self.name = self.__class__.__name__
        self.frac = frac
        self.color = color

    def __lt__(self, other):
        return self.frac < other.frac


class Steel:
    """
    A Steel with many elements.
    """
    def __init__(
            self,
            elements: List[Element],
            year: int,
            name: str = 'None',
    ):
        self.name = name
        self.year = year
        self.elements = sorted(elements)
        self.total_frac = sum([e.frac for e in self.elements])

    def __lt__(self, other):
        return self.year < other.year

    def __len__(self):
        return len(self.elements)


class Steels:
    """
    A list of steels to plot.
    """
    def __init__(
            self,
            steels: List[Steel],
    ):
        self.steels = sorted(steels)

    def __len__(self):
        return len(self.steels)


# Define each element
class C(Element):
    def __init__(self, frac: float):
        super().__init__(
            frac=frac,
            color='orange',
        )


class Cr(Element):
    def __init__(self, frac: float):
        super().__init__(
            frac=frac,
            color='blue',
        )


class Ni(Element):
    def __init__(self, frac: float):
        super().__init__(
            frac=frac,
            color='green',
        )


# Define the steels
steel_list = Steels(
    steels=[
        Steel(
            year=1865,
            elements=[
                C(frac=3),
                Cr(frac=2),
            ]
        ),
        Steel(
            year=1888,
            elements=[
                C(frac=1),
                Ni(frac=1),

            ]
        )
    ]
)


def run():
    """
    Plot the steel data.
    :return: None
    """

    # Create the plot
    figure: plt.Figure = plt.figure()
    ax: plt.Axes = figure.add_subplot()

    # For each steel
    for i, i_steel in enumerate(steel_list.steels):

        # Define the current base of the stack.
        base = 0

        # For each component
        for j, element in enumerate(i_steel.elements):

            # Add the element
            rect = patches.Rectangle(
                (i, base),
                0.1,
                element.frac,
                facecolor=element.color,
            )
            ax.add_patch(rect)

            # Update the base of the stack
            base += element.frac

    # Format
    ax.set_xlim(-1, len(steel_list))
    ax.set_ylim(-1, max([s.total_frac for s in steel_list.steels]) + 1)

    # Save
    name = os.path.basename(__file__).split('.')[0]
    figure.set_dpi(300)
    figure.savefig(f'{name}.png')
    figure.savefig(f'{name}.svg')


if __name__ == '__main__':
    run()
