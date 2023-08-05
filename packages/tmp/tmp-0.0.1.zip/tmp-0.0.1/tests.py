import unittest


class TestCase(unittest.TestCase):
    """
    """

    def test_tmp(self):
        """
        """

        from tmp import tmp
        import os
        tmpdir = tmp()
        os.listdir(tmpdir)
