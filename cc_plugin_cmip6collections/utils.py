import os


class StructuredDataset(object):

    def __init__(self, root):
        if not os.path.isdir(root):
            raise Exception("{} is not a directory".format(root))

        self._root = os.path.join(root, '')
        self._dataset = self._walk_directory(root)

    @classmethod
    def _walk_directory(cls, basedir):
        dataset = []
        for root, dirs, files in os.walk(basedir):
            for filename in files:
                if filename.endswith(".nc"):
                    dataset.append(os.path.join(root, filename))
        return dataset

    def get_root(self):
        return self._root

    def get_filepaths(self):
        return self._dataset
