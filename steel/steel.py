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
            frac: float,
            color: str,
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
        self.count = len(self.elements)

    def __lt__(self, other):
        return self.year < other.year


class Steels:
    """
    A list of steels to plot.
    """
    def __init__(
            self,
            steels: List[Steel],
    ):
        self.steels = sorted(steels)


# Define each element
class C(Element):
    def __init__(self, frac: float):
        super().__init__(
            frac=frac,
            color='#555555',
        )


class Cr(Element):
    def __init__(self, frac: float):
        super().__init__(
            frac=frac,
            color='#333333',
        )


class Ni(Element):
    def __init__(self, frac: float):
        super().__init__(
            frac=frac,
            color='#777777',
        )


# Define the steels
steel = Steels(
    steels=[
        Steel(
            year=1865,
            elements=[
                C(frac=1),
                Cr(frac=2),
            ]
        ),
        Steel(
            year=1888,
            elements=[
                C(frac=1),

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

    # Save


if __name__ == '__main__':
    run()