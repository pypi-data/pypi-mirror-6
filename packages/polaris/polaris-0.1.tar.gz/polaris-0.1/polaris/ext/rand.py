"""
    polaris.ext.rand
    ~~~~~~~~~~~~~~~~

    :copyright: (c) 2013 Eleme, http://polaris.eleme.io
    :license: MIT

    The rand extension will generate random series and dataframe based on args.
    This extension is mainly for example demo.
"""

import numpy as np
import pandas as pd

from polaris.ext import PolarisExtension


class Rand(PolarisExtension):
    """Generate random series or dataframe
    """

    def __init__(self, **kwargs):
        pass

    def get(self, x=5, y=1, index=None, columns=None, **kwargs):
        """Generate a matrix based on x, y, z
        """
        x, y = int(x), int(y)
        df = pd.DataFrame(np.random.randint(1, 10, size=(x, y)))
        if columns:
            df.columns = columns
        if index:
            df.set_index(index)
        return df
