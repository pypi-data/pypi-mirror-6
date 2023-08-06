import logging
import numpy as np
from scipy.io.matlab import loadmat
#from sktensor.rescal import rescal_als
from sktensor.rescal3 import rescal3_als
from sktensor.sptensor import fromarray

# Set logging to INFO to see RESCAL information
logging.basicConfig(level=logging.DEBUG)

# Load Matlab data and convert it to dense tensor format
X = fromarray(loadmat('data/kinships/alyawarradata.mat')['Rs'])
#X = [lil_matrix(T[:, :, k]) for k in range(T.shape[2])]

# Decompose tensor using RESCAL-ALS
#A, R, fit, itr, exectimes = rescal_als(X, 100, init='nvecs', lambda_A=10, lambda_R=10)

G, A, R = rescal3_als(X, 100, 10, init='nvecs', dtype=np.float)
