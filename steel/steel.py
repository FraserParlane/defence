import matplotlib.pyplot as plt
from typing import List
import pandas as pd
import numpy as np

# A plot of the complexity of steel over time. See:
# https://docs.google.com/document/d/1ZkReceEGZomda2GGzVP1f2HIrID8KVW9nJ3OUeg8woA/edit


# Define the compositions of the steels
class Element:
    """
    One component of a steel.
    """
    def __init__(
            self,
            name: str,
            frac: float,
            color: str,
    ):
        self.name = name
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
            name: str,
            year: int,
            components: List[Element]
    ):
        self.name = name
        self.year = year
        self.components = sorted(components)
        self.count = len(self.components)

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
            name='C',
            frac=frac,
            color='#555555',
        )


class Cr(Element):
    def __init__(self, frac: float):
        super().__init__(
            name='Cr',
            frac=frac,
            color='#123456',
        )


# Define the steels
steel = Steels(
    steels=[

    ]
)


if __name__ == '__main__':
    print(steel)