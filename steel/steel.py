import matplotlib.patches as patches
import matplotlib.pyplot as plt
from typing import List
from colors import c
import numpy as np
import os

# A plot of the complexity of steel over time. See:
# https://docs.google.com/document/d/1ZkReceEGZomda2GGzVP1f2HIrID8KVW9nJ3OUeg8woA/edit


# Define the compositions of the steels
class Element:
    """
    One element of a steel.
    """
    def __init__(self):
        self.name = self.__class__.__name__


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
        self.elements = elements

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

        # Store each element in the order they appear
        self.elements = []
        for i_steel in self.steels:
            for element in i_steel.elements:
                if element.name not in self.elements:
                    self.elements.append(element.name)
        self.elements = np.array(self.elements)

    def __len__(self):
        return len(self.steels)


# Define each element
class C(Element):
    def __init__(self):
        super().__init__()


class Cr(Element):
    def __init__(self):
        super().__init__()


class Ni(Element):
    def __init__(self):
        super().__init__()


class V(Element):
    def __init__(self):
        super().__init__()


class Mn(Element):
    def __init__(self):
        super().__init__()


class P(Element):
    def __init__(self):
        super().__init__()


class S(Element):
    def __init__(self):
        super().__init__()


class Si(Element):
    def __init__(self):
        super().__init__()


class Cu(Element):
    def __init__(self):
        super().__init__()


# Define the steels
steel_list = Steels(
    steels=[
        Steel(
            year=1865,
            elements=[C(), Cr()]
        ),
        Steel(
            year=1888,
            elements=[C(), Ni()]
        ),
        Steel(
            year=1900,
            elements=[C(), Ni(), Cr()]
        ),
        Steel(
            year=1900,
            elements=[C(), Cr(), V()]
        ),
        Steel(
            year=2000,
            elements=[Cr(), Ni(), Mn(), P(), S(), Si(), C()]
        ),
        Steel(
            year=2001,
            name='Cor-Ten ASTM A242',
            elements=[C(), Si(), Mn(), P(), S(), Cr(), Cu(), Ni()]
        ),
Steel(
            year=2001,
            name='Cor-Ten ASTM A588',
            elements=[C(), Si(), Mn(), P(), S(), Cr(), Cu(), V(), Ni()]
        )
    ]
)


def run():
    """
    Plot the steel data.
    :return: None
    """

    # Create the plot
    figure: plt.Figure = plt.figure(
        figsize=(10, 5),
        dpi=300,
    )
    ax: plt.Axes = figure.add_subplot()

    # Add the names of each element
    for i, e in enumerate(steel_list.elements):
        ax.text(
            i,
            0.5,
            e,
            horizontalalignment='center',
        )

    # For each steel
    for i, i_steel in enumerate(steel_list.steels):

        # Define the y position for the steel
        y = -i

        # For each component
        for j, element in enumerate(i_steel.elements):

            # Get x position of element
            x = np.where(steel_list.elements == element.name)[0][0]

            # Add the point to the plot
            circle = patches.Circle(
                (x, y),
                radius=0.175,
                facecolor=c.pink.i400,
                edgecolor=c.pink.i700,
                linewidth=2,
            )
            ax.add_patch(circle)

            # Add name, year, components
            ax.text(
                -1.5,
                y,
                f'{i_steel.name} ({i_steel.year})',
                verticalalignment='center',
                horizontalalignment='right',
            )
            ax.text(
                -1,
                y,
                str(len(i_steel)),
                verticalalignment='center',
            )

    # Format
    ax.set_xlim(-4, len(steel_list.elements))
    ax.set_ylim(-len(steel_list), 1)
    ax.set_aspect('equal')
    for pos in ['left', 'right', 'top', 'bottom']:
        ax.spines[pos].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

    # Save
    name = os.path.basename(__file__).split('.')[0]
    figure.set_dpi(300)
    figure.savefig(f'{name}.png')
    figure.savefig(f'{name}.svg')


if __name__ == '__main__':
    run()
