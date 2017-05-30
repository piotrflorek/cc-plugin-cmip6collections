import os
import unittest
from rainbowrunners.runner import NyanCatRunner

if __name__ == "__main__":
    this_dir = os.path.dirname(__file__)
    suite = unittest.TestLoader().discover(this_dir)
    NyanCatRunner().run(suite)
