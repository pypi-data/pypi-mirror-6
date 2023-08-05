# Authors: Denis Engemann <d.engemann@fz-juelich.de>
#
# License: BSD Style.

import numpy as np

from ...utils import get_config, verbose
from ...fixes import partial
from ..utils import has_dataset, _data_path, _doc

has_spm_data = partial(has_dataset, name='spm')

@verbose
def data_path(path=None, force_update=False, update_path=True,
              download=True, verbose=None):
    return _data_path(path=path, force_update=force_update,
                      update_path=update_path, name='spm',
                      download=download,
                      verbose=verbose)

data_path.__doc__ = _doc.format(name='spm',
                                conf='MNE_DATASETS_SPM_DATA_PATH')

# Allow forcing of sample dataset skip (for tests) using:
# `make test-no-sample`
skip_spm = get_config('MNE_SKIP_SPM_DATASET_TESTS', 'false') == 'true'
has_spm_data = has_dataset('spm')
requires_spm_data = np.testing.dec.skipif(not has_spm_data
                                          or skip_spm,
                                          'Requires spm dataset')
