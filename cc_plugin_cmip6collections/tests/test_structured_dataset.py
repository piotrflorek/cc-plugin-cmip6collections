import os
import unittest
from cc_plugin_cmip6collections.utils import StructuredDataset


class StructuredDatasetTestCase(unittest.TestCase):

    def setUp(self):
        self._dataset_root = os.path.join(
            os.path.dirname(__file__), 'data', 'dataset'
        )

    def test_dir_walking(self):
        ds = StructuredDataset(self._dataset_root)
        result = ds.get_filepaths()
        self.assertListEqual(result, [
            os.path.join(
                self._dataset_root, 'dir1', 'dir2', 'dir3', 'foo.nc'
            ),
            os.path.join(
                self._dataset_root, 'dir1', 'dir2', 'dir3b', 'foobar.nc' 
            ),
            os.path.join(
                self._dataset_root, 'dir4', 'bar.nc'
            )
        ])

