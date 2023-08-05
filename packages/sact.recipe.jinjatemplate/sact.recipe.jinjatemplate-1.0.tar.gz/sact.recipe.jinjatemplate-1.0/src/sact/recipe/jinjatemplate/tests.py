import os
import unittest


class TestRecipe(unittest.TestCase):
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

    def test_simple(self):
        result_dir = os.path.abspath(os.path.join(self.CURRENT_DIR, "templates"))
        file_1_path = os.path.join(result_dir, "test1.result")
        file_2_path = os.path.join(result_dir, "test2.result")
        file_1 = open(file_1_path).read()
        file_2 = open(file_2_path).read()

        self.assertEquals(file_1, file_2)
