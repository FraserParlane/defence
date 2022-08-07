from sklearn.gaussian_process import GaussianProcessRegressor
import matplotlib.pyplot as plt
import numpy as np

# Create two surfaces to compare grid and optimization sampling.


def run():

    # Create noisy training data and fit GP
    n_train = 10
    np.random.seed(1)
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




if __name__ == '__main__':
    run()
