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


if __name__ == '__main__':
    data = read_data()
    print(data)
