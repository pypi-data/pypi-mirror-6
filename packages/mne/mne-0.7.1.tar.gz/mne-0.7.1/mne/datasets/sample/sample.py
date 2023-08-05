# Authors: Alexandre Gramfort <gramfort@nmr.mgh.harvard.edu>
#          Martin Luessi <mluessi@nmr.mgh.harvard.edu>
#          Eric Larson <larson.eric.d@gmail.com>
# License: BSD Style.

import numpy as np

from ...utils import get_config, verbose
from ..utils import has_dataset, _data_path, _doc

@verbose
def data_path(path=None, force_update=False, update_path=True,
              download=True, verbose=None):
    return _data_path(path=path, force_update=force_update,
                      update_path=update_path, name='sample',
                      download=download,
                      verbose=verbose)

data_path.__doc__ = _doc.format(name='sample',
                                conf='MNE_DATASETS_SAMPLE_PATH')

# Allow forcing of sample dataset skip (for tests) using:
# `make test-no-sample`
has_sample_data = has_dataset('sample')
skip_sample = get_config('MNE_SKIP_SAMPLE_DATASET_TESTS', 'false') == 'true'
requires_sample_data = np.testing.dec.skipif(not has_dataset('sample')
                                             or skip_sample,
                                             'Requires sample dataset')
